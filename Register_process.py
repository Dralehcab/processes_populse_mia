from populse_mia.pipeline_manager.process_mia import ProcessMIA
import traits.api as traits
from traits.api import CArray
import os
import numpy as np
import sys

sys.path.append('/home/broche/Code/Python/processes_populse_mia/utils')
from NiftiHeaderManagement import NiftiHeaderManagement


class RegisterProcess(ProcessMIA):
    """
    Perform Elastic BSpline Registration in between 2 images
    """

    def __init__(self):
        super(RegisterProcess, self).__init__()



        #Image Inputs

        fix_image_desc = "Input Fixed Image"
        trait_array = CArray(output=False, optional=False, desc=fix_image_desc)
        self.add_trait("fix_image",trait_array)
        self.add_trait("fix_image_jason", traits.File(output=False))

        mov_image_desc = "Input Moving Image"
        trait_array = CArray(output=False, optional=False, desc=mov_image_desc)
        self.add_trait("mov_image", trait_array)
        self.add_trait("mov_image_jason", traits.File(output=False))

        fix_rigid_image_desc = "Input fixed Initial Rigid Transform"
        trait_array = CArray(output=False, optional=True, desc=fix_rigid_image_desc)
        self.add_trait("fix_rigid_image", trait_array)
        self.add_trait("fix_rigid_jason", traits.File(output=False,optional=True))

        mov_rigid_image_desc = "Input moving Initial Rigid Transform"
        trait_array = CArray(output=False, optional=True, desc=mov_rigid_image_desc)
        self.add_trait("mov_rigid_image", trait_array)
        self.add_trait("mov_rigid_jason", traits.File(output=False,optional=True))

        # Initial Transform

        self.add_trait("initial_transform", traits.Enum('None','Geometry', 'Moments', output=False, optional=True,
                                    desc='Method used For Initial Transfrom (either "None", "Geometry" or "Moments")'))

        #Grid Size

        self.add_trait("grid_size", traits.List(traits.Float(), [20.0, 20.0, 20.0], output=False, optional=True,
                                           desc='Registration Grid Nodes Interspace In X,Y and Z direction'))

        #Gradient Image

        self.add_trait("gradient_flag",traits.Enum('True', 'False', output=False, optional=True,
                                                   desc='Use the gradient Image to Perform Registration'))

        # Metric

        self.add_trait("metric_method", traits.Enum('Means Squares', 'Correlation', 'Demons',
                                "Joint Histogram Mutual Information","Mattes Mutual Information",
                                "Neighborhood Correlation (ANTs)", output=False, optional=True,
                                desc='Method used For Metric Calculation:(Means Squares, Correlation, Demons,' 
                                ' Joint Histogram Mutual Information,Mattes Mutual Information,' 
                                'Neighborhood Correlation (ANTs)) '))

        self.add_trait("metric_parameters", traits.List(traits.Float(), [1.0, 1.0], output=False, optional=True,
                                           desc='List of metric parameters (see documentation for more details)'))

        self.add_trait("sampling_strategy", traits.Enum('None', 'Regular', 'Random', output=False, optional=True,
                                           desc='Technique to reduce number of points tested for metric calculation'
                                            '("None","Regular","Random")'))

        self.add_trait("sampling_strategy_parameters", traits.Float(0.5, output=False, optional=True,
                                           desc='Parameter for points tested reduction'))



        # Optimizer

        self.add_trait("optimizer_method", traits.Enum('Regular Step Gradient Descent', 'Gradient Descent',
                        'Gradient Descent Line Search','Conjugate Gradient Line Search','LBFGSB','Powell','Amoeba',
                        output=False, optional=True,
                        desc='Method used For Optimizer:("Regular Step Gradient Descent","Gradient Descent",'
                        '"Conjugate Gradient Line Search","LBFGSB","Powell","Amoeba")'))


        self.add_trait("optimizer_parameters", traits.List(traits.Float(), [1.0, 1.0], output=False, optional=True,
                                           desc='List of optimizer parameters (see documentation for more details)'))



        self.add_trait("learning_rate_estimation", traits.Enum('Never', 'Once', 'Each Iteration', output=False, optional=True,
                        desc='Frequency to reevaluate learning rate during registration("Never","Once","EachIteration")'))

        self.add_trait("maximum_learning_rate", traits.Float(20.0, output=False, optional=True,
                        desc='Maximum Learning Rate allowed if reestimated'))


        self.add_trait("optimizer scale method ", traits.Enum('None', 'Index Shift', 'Jacobian','Physical Shift',
                        output=False, optional=True,
                        desc='Define the automatic Method to Scale the optizer parameters ("None", "Index Shift",'
                        ' "Jacobian","Physical Shift")'))

        self.add_trait("optimizer_scale_paramters", traits.List(traits.Float(), [1.0, 1.0], output=False, optional=True,
                        desc='List of optimizer scale parameters (see documentation for more details)'))



        #Interpolator

        self.add_trait("interpolator", traits.Enum('Nearest neighbor', 'Linear Interpolation', 'BSpline','Gaussian',
                                        'Label Gaussian','Hamming Windowed Sinc','Cosine Windowed Sinc',
                                        'Welch Windowed Sinc','Lanczos Windowed Sinc','Blackman Windowed Sinc',
                                        output=False, optional=True,
                                        desc='Interpolator:("Nearest neighbor", "Linear Interpolation", "BSpline",'
                                        '"Gaussian","Label Gaussian","Hamming Windowed Sinc","Cosine Windowed Sinc",'
                                             '"Welch Windowed Sinc","Lanczos Windowed Sinc","Blackman Windowed Sinc")'))

        #Scaling

        self.add_trait("image_scaling", traits.List(traits.Float(), [16.0, 8.0,4.0,2.0,1.0], output=False, optional=True,
                                        desc='Image Downscale To perform Consecutive Registration'))

        self.add_trait("image_smoothing", traits.List(traits.Float(), [0.0, 0.0, 0.0, 0.0, 0.0], output=False, optional=True,
                                        desc='Smoothing Factor for each Resolution Step'))

        #Ouputs
        registered_image_desc = "Ouput Image Registered"
        trait_array = CArray(output=True, optional=False, desc=registered_image_desc)
        self.add_trait("registered_image", trait_array)
        self.add_trait("registered_image_jason", traits.File(output=True, optional=False))


    def list_outputs(self):
        super(RegisterProcess, self).list_outputs()
        return {"<undefined>":[]},{}



    def _run_process(self):


        fix_image_desc = "Input Fixed Image"
        trait_array = CArray(output=False, optional=False, desc=fix_image_desc)
        self.add_trait("fix_image",trait_array)
        self.add_trait("fix_image_jason", traits.File(output=False))

        mov_image_desc = "Input Moving Image"
        trait_array = CArray(output=False, optional=False, desc=mov_image_desc)
        self.add_trait("mov_image", trait_array)
        self.add_trait("mov_image_jason", traits.File(output=False))

        fix_rigid_image_desc = "Input fixed Initial Rigid Transform"
        trait_array = CArray(output=False, optional=True, desc=fix_rigid_image_desc)
        self.add_trait("fix_rigid_image", trait_array)
        self.add_trait("fix_rigid_jason", traits.File(output=False,optional=True))

        mov_rigid_image_desc = "Input moving Initial Rigid Transform"
        trait_array = CArray(output=False, optional=True, desc=mov_rigid_image_desc)
        self.add_trait("mov_rigid_image", trait_array)
        self.add_trait("mov_rigid_jason", traits.File(output=False,optional=True))


        image_matrix = [sels.f