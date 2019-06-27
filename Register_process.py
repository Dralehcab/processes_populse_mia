from populse_mia.pipeline_manager.process_mia import ProcessMIA
import traits.api as traits
from traits.api import CArray
import os
import numpy as np
import sys
import shutil

sys.path.append('/home/broche/Code/Python/processes_populse_mia/image_processing/')
sys.path.append('/home/broche/Code/Python/processes_populse_mia/utils/')
from RegistrationIP import Registering
from file_management import copy_rename



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

        self.add_trait("grid_size", traits.List(traits.Float(), [40.0, 40.0, 40.0], output=False, optional=True,
                                           desc='Registration Grid Nodes Interspace In X,Y and Z direction'))

        #Gradient Image

        self.add_trait("gradient_flag",traits.Enum('true', 'false', output=False, optional=True,
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


        self.add_trait("optimizer_parameters", traits.List(traits.Float(), [1.0,0.1,10,0.5,0.0001,0,0.0],
                        output=False, optional=True,
                        desc='List of optimizer parameters (see documentation for more details)'))



        self.add_trait("learning_rate_estimation", traits.Enum('Never', 'Once', 'Each Iteration', output=False, optional=True,
                        desc='Frequency to reevaluate learning rate during registration("Never","Once","EachIteration")'))

        self.add_trait("maximum_learning_rate", traits.Float(20.0, output=False, optional=True,
                        desc='Maximum Learning Rate allowed if reestimated'))


        self.add_trait("optimizer_scale_method", traits.Enum('None', 'Index Shift', 'Jacobian','Physical Shift',
                        output=False, optional=True,
                        desc='Define the automatic Method to Scale the optizer parameters ("None", "Index Shift",'
                        ' "Jacobian","Physical Shift")'))

        self.add_trait("optimizer_scale_parameters", traits.List(traits.Float(), [1.0, 1.0], output=False, optional=True,
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

        self.add_trait("image_scaling", traits.List(traits.Float(), [16, 8, 4,2,1], output=False, optional=True,
                                        desc='Image Downscale To perform Consecutive Registration'))

        self.add_trait("image_smoothing", traits.List(traits.Float(), [0, 0, 0, 0, 0], output=False, optional=True,
                                        desc='Smoothing Factor for each Resolution Step'))

        #Ouputs
        registered_image_desc = "Output Image Registered"
        trait_array = CArray(output=True, optional=True, desc=registered_image_desc)
        self.add_trait("registered_image", trait_array)
        self.add_trait("registered_image_jason", traits.File(output=True, optional=True))


        """
        chess_image_desc = "Output Image Chess Comparison"
        trait_array = CArray(output=True, optional=True, desc=chess_image_desc)
        self.add_trait("chess_image", trait_array)
        self.add_trait("chess_image_jason", traits.File(output=True, optional=True))

        vector_image_desc = "Output Image Vector Field"
        trait_array = CArray(output=True, optional=True, desc=vector_image_desc)
        self.add_trait("vector_image", trait_array)
        self.add_trait("vector_image_jason", traits.File(output=True, optional=True))

        self.add_trait("registration_info_file", traits.File(output=True, optional=True))
        """


    def list_outputs(self):
        super(RegisterProcess, self).list_outputs()
        # Generating the filename by hand

        if not self.fix_image_jason:
            print('"in_file" plug is mandatory for Convert process')
            return {}
        else:
            path, filename = os.path.split(self.fix_image_jason)
            out_filename = 'R_' + filename
            output_dict = {'registered_image_jason': os.path.join(path, out_filename)}

        inheritance_dict =  {output_dict['registered_image_jason']: self.fix_image_jason}

        return output_dict, inheritance_dict


    def _run_process(self):


        print('In process')
        # Initialising parameters dictionnary
        self.dicPar = {'Grid': [0, 0, 0], 'Inputs': {}, 'Outputs': {}, 'Metric': {}, 'Optimizer': {},
                       'Interpolator': {}, 'Scaling': []}


        self.dicPar['Metric']['Sampling'] =  {'Method':'None','Percentage': 0.5}
        self.dicPar['Optimizer']['Par'] = [0,1,2,3,4,5,6,7,8,9,10]


        # Setting Image Array and Info
        if self.fix_image != [] and self.mov_image != []:

            image_matrix = [self.fix_image,self.mov_image,self.fix_rigid_image,self.mov_rigid_image]
            image_info_file = [self.fix_image_jason,self.mov_image_jason,self.fix_rigid_jason,self.mov_rigid_jason]

        else:
            print("Missing fixed or moving Image")



        self.dicPar['Inputs']['Images_Array'] = image_matrix
        self.dicPar['Inputs']['Image_info_files'] = image_info_file

        # Setting Initial Transform

        if self.initial_transform in ['None', 'Geometry', 'Moments']:
            self.dicPar['Inputs']['InitT'] = self.initial_transform
        else:
            print('Unrecognized Initial Transform Method')
            input()


        #Setting Grid Size

        if len(self.grid_size) == 3:
            self.dicPar['Grid'] = np.array(self.grid_size)

        else:
            print('Uncorrect Grid Vector')
            print('Setting Grid to default value [40.0,40.0,40.0]')
            input()
            self.dicPar['Grid'] = [40.0,40.0,40.0]

        #Setting Gradient Image Flag

        if self.gradient_flag == "true":
            self.dicPar['Metric']['GradF'] = 1
            self.dicPar['Metric']['GradM'] = 1
        else:
            self.dicPar['Metric']['GradF'] = 0
            self.dicPar['Metric']['GradM'] = 0

        # Setting the Metric Parameters

        list_method = ["Means Squares","Correlation","Demons","Joint Histogram Mutual Information",
                       "Mattes Mutual Information","Neighborhood Correlation (ANTs)"]

        if self.metric_method in list_method:
            self.dicPar['Metric']['Method'] = self.metric_method
            self.dicPar['Metric']['Par'] = np.array(self.metric_parameters)
        else:
            print("Unrecognized Metric Method")
            print('Setting Metric to Default Method : MeanSquare')
            input()
            self.dicPar['Metric']['Method'] = "Means Squares"

        self.dicPar['Metric']['Par'] = self.metric_parameters

        list_method = ["None", "Regular", "Random"]

        if self.sampling_strategy in list_method:
            self.dicPar['Metric']['Sampling']['Method'] = self.sampling_strategy
        else:
            print("Unrecognized Sampling Strategy Method")
            print('Setting Sampling Strategy to Default Method : None')
            input()
            self.dicPar['Metric']['Sampling']['Method'] = 'None'

        self.dicPar['Metric']['Sampling']['Percentage'] = self.sampling_strategy_parameters

        # Setting the Optimizer
        list_method = ['Regular Step Gradient Descent', 'Gradient Descent','Gradient Descent Line Search',
                       'Conjugate Gradient Line Search','LBFGSB', 'Powell', 'Amoeba',]

        if self.optimizer_method in list_method:
            self.dicPar['Optimizer']['Method'] = self.optimizer_method
            self.dicPar['Optimizer']['Par'] = self.optimizer_parameters

        else:
            print("Unrecognized Optimizer Method")
            print('Setting Optimizer Method to Default Method : "Regular Step Gradient Descent":')
            self.dicPar['Optimizer']['Method'] = "Regular Step Gradient Descent"
            self.dicPar['Optimizer']['Par'] = [1.0, 0.1, 10, 0.5, 0.0001, 0, 0.0]
            input()


        list_method = ['Never', 'Once', 'Each Iteration']

        if self.learning_rate_estimation in list_method:
            if  self.learning_rate_estimation == "Never":
                self.dicPar['Optimizer']['Par'].append(0)
                self.dicPar['Optimizer']['Par'].append(self.maximum_learning_rate)
            elif self.learning_rate_estimation == "Once":
                self.dicPar['Optimizer']['Par'].append(1)
                self.dicPar['Optimizer']['Par'].append(self.maximum_learning_rate)
            elif self.learning_rate_estimation == "Each Iteration":
                self.dicPar['Optimizer']['Par'].append(2)
                self.dicPar['Optimizer']['Par'].append(self.maximum_learning_rate)

        else:
            print("Unrecognized Learning Rate Method")
            print('Setting Learning Rate Method to Default value : "Never":')
            self.dicPar['Optimizer']['Par'].append(0)
            self.dicPar['Optimizer']['Par'].append(20.0)
            input()

        list_method = ['None', 'Index Shift', 'Jacobian','Physical Shift']

        if self.optimizer_scale_method in list_method:
            self.dicPar['Optimizer']['MethodScaling'] = self.optimizer_scale_method
            self.dicPar['Optimizer']['ScalePar'] = self.optimizer_scale_parameters

        else:
            print("Unrecognized Optimizer Scale Method: ")
            print('Setting  Optimizer Scale Method to Default value : "None":')
            self.dicPar['Optimizer']['MethodScaling'] = 'None'
            input()


        # Setting Interpolator
        list_method = ['Nearest neighbor', 'Linear Interpolation', 'BSpline','Gaussian','Label Gaussian',
                       'Hamming Windowed Sinc','Cosine Windowed Sinc','Welch Windowed Sinc','Lanczos Windowed Sinc',
                       'Blackman Windowed Sinc']

        if self.interpolator in list_method:
            self.dicPar['Interpolator'] = self.interpolator
        else:
            print("Unrecognized Interpolator")
            print('Setting Interpolator to Default Method : "Nearest neighbor"')
            self.dicPar['Optimizer']['Method'] = 'Nearest neighbor'
            input()

        #Setting Scaling

        if len(self.image_scaling ) > 0:
            self.dicPar['Scaling'] = self.image_scaling
        else:
            print("Unrecognized Registration Scaling")
            print('Setting Scaling to : [16,8,4,2,1]')
            self.dicPar['Scaling'] = [16,8,4,2,1]
            input()


        if len(self.image_smoothing) != len(self.image_scaling):
            self.dicPar['Scaling'] = self.image_scaling
        else:
            print("Unrecognized Registration Smoothing")
            print('Setting Smoothing to : [0,0,0,0,0]')
            self.dicPar['Smoothing'] = [0,0,0,0,0]
            input()


        self.R = Registering(self.dicPar)
        print('Executing')
        self.R.Execute()
        print(self.R.reg_method.GetMetricValue())
        self.registered_image = self.R.returnNumpyImage()
        self.vector_image = self.R.transformOut
        self.chess_image =  self.R.chessImage

        print('Starting Copy Rename File')
        print(self.fix_image_jason)
        print(self.registered_image_jason)

        path, filename = os.path.split(self.fix_image_jason)
        shutil.copy(self.fix_image_jason, path + 'tmp.json' )
        shutil.move(path + 'tmp.json',self.registered_image_jason)

        """
        path, filename = os.path.split(self.fix_image_jason)
        shutil.copy(self.fix_image_jason, path + 'tmp.json' )
        shutil.move(path + 'tmp.json',self.vector_image_jason)

        path, filename = os.path.split(self.fix_image_jason)
        shutil.copy(self.fix_image_jason, path + 'tmp.json')
        shutil.move(path + 'tmp.json',self.chess_image_jason)

        print('Done')
        """

if __name__ == "__main__":

    a = ProcessMIA()
    dicPar = {'Grid': [10, 10, 10], 'Inputs': {}, 'Outputs': {}, 'Metric': {}, 'Optimizer': {},'Interpolator': {}, 'Scaling': []}
    R = Registration(a)
    R._run


