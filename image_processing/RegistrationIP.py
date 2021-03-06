# -*- coding: utf-8 -*-
"""
Created on Fri Dec 09 10:14:27 2016

@author: broche
"""

import SimpleITK as sitk
import numpy as np


def imageFromNumpyToITK(vol):
    return sitk.GetImageFromArray(vol)


def imageFromITKToNumpy(vol):
    return sitk.GetArrayFromImage(vol)


class Registering():

    def __init__(self, dicPar):

        self.dicPar = dicPar

        self.ImageStack = self.dicPar['Inputs']['Images_Array']

        self.ImageFixe = []
        self.ImageMoving = []
        self.MaskFixe = []
        self.MaskMoving = []

        """Init registering object """
        self.reg_method = sitk.ImageRegistrationMethod()
        """Init Metric """
        self.initMetric()
        """Optimizer"""
        self.initOptimizer()
        """Interpolator"""
        self.initInterpolator()
        """ Scaling """
        self.initScaling()

        """ Set Inputs"""
        self.setImages()
        self.initIntitialTransform()

    def setImages(self):

        self.ImageFixe = imageFromNumpyToITK(self.ImageStack[0]*1000.0)
        self.ImageMoving = imageFromNumpyToITK(self.ImageStack[1]*1000.0)


        if self.dicPar['Inputs']['InitT'] != 'None':
            self.ImageInitFixe = imageFromNumpyToITK(self.ImageStack[2]*1000.0)
            self.ImageInitMoving = imageFromNumpyToITK(self.ImageStack[3]*1000.0)



    def initIntitialTransform(self):

        if self.dicPar['Inputs']['InitT'] != "None":
            if self.dicPar['Inputs']['InitT'] == "Geometry":
                self.init_t = sitk.CenteredTransformInitializer(self.ImageInitFixe, self.ImageInitMoving,
                                                                sitk.Euler3DTransform(),
                                                                sitk.CenteredTransformInitializerFilter.GEOMETRY)
            elif self.dicPar['Inputs']['InitT'] == "Moments":
                self.init_t = sitk.CenteredTransformInitializer(self.ImageInitFixe, self.ImageInitMoving,
                                                                sitk.Euler3DTransform(),
                                                                sitk.CenteredTransformInitializerFilter.MOMENTS)

            self.ImageMoving = sitk.Resample(self.ImageMoving, self.ImageFixe, self.init_t, self.interpolator, 0.0,
                                             self.ImageMoving.GetPixelIDValue())



        x_grid_size = self.dicPar['Grid'][0]
        y_grid_size = self.dicPar['Grid'][1]
        z_grid_size = self.dicPar['Grid'][2]

        grid_physical_spacing = [x_grid_size, y_grid_size, z_grid_size]
        image_physical_size = [size * spacing for size, spacing in
                               zip(self.ImageFixe.GetSize(), self.ImageFixe.GetSpacing())]
        mesh_size = [int(image_size / grid_spacing + 0.5) for image_size, grid_spacing in
                     zip(image_physical_size, grid_physical_spacing)]
        self.initial_transform = sitk.BSplineTransformInitializer(image1=self.ImageFixe,
                                                                  transformDomainMeshSize=mesh_size, order=3)
        self.reg_method.SetInitialTransform(self.initial_transform)

    def initMetric(self):

        print(self.dicPar)

        """ Metric """
        if self.dicPar['Metric']['Method'] == "Means Squares":
            self.reg_method.SetMetricAsMeanSquares()

        elif self.dicPar['Metric']['Method'] == "Correlation":
            self.reg_method.SetMetricAsCorrelation()

        elif self.dicPar['Metric']['Method'] == "Demons":
            par1 = float(self.dicPar['Metric']['Par'][0])
            self.reg_method.SetMetricAsDemons(par1)

        elif self.dicPar['Metric']['Method'] == "Joint Histogram Mutual Information":
            par1 = int(self.dicPar['Metric']['Par'][0])
            par2 = float(self.dicPar['Metric']['Par'][1])
            self.reg_method.SetMetricAsJointHistogramMutualInformation(par1, par2)

        elif self.dicPar['Metric']['Method'] == "Mattes Mutual Information":
            par1 = int(self.dicPar['Metric']['Par'][0])
            self.reg_method.SetMetricAsMattesMutualInformation(par1)
        elif self.dicPar['Metric']['Method'] == "Neighborhood Correlation (ANTs)":
            par1 = int(self.dicPar['Metric']['Par'][0])
            self.reg_method.SetMetricAsANTSNeighborhoodCorrelation(par1)

        if self.dicPar['Metric']['Sampling']['Method'] != 'None':

            if self.dicPar['Metric']['Sampling']['Method'] != 'Random':
                self.reg_method.SetMetricSamplingStrategy(self.reg_method.RANDOM)
            if self.dicPar['Metric']['Sampling']['Method'] != 'Regular':
                self.reg_method.SetMetricSamplingStrategy(self.reg_method.REGULAR)
            perc = float(self.dicPar['Metric']['Sampling']['Percentage'])
            self.reg_method.SetMetricSamplingPercentage(perc)

        flag_grad_fx_I = int(self.dicPar['Metric']['GradF'])
        flag_grad_mv_I = int(self.dicPar['Metric']['GradM'])

        self.reg_method.SetMetricUseFixedImageGradientFilter(bool(flag_grad_fx_I))
        self.reg_method.SetMetricUseMovingImageGradientFilter(bool(flag_grad_mv_I))

    def initOptimizer(self):
        """ Optimizer """

        if self.dicPar['Optimizer']['Method'] == "Regular Step Gradient Descent":

            par1 = float(self.dicPar['Optimizer']['Par'][0])
            par2 = float(self.dicPar['Optimizer']['Par'][1])
            par3 = int(self.dicPar['Optimizer']['Par'][2])
            par4 = float(self.dicPar['Optimizer']['Par'][3])
            par5 = float(self.dicPar['Optimizer']['Par'][4])

            if int(self.dicPar['Optimizer']['Par'][5]) == 0:
                par6 = self.reg_method.Never
            elif int(self.dicPar['Optimizer']['Par'][5]) == 1:
                par6 = self.reg_method.Once
            elif int(self.dicPar['Optimizer']['Par'][5]) == 2:
                par6 = self.reg_method.EachIteration

            par7 = float(self.dicPar['Optimizer']['Par'][6])

            self.reg_method.SetOptimizerAsRegularStepGradientDescent(par1, par2, par3, par4, par5, par6, par7)

        elif self.dicPar['Optimizer']['Method'] == "Gradient Descent":

            par1 = float(self.dicPar['Optimizer']['Par'][0])
            par2 = int(self.dicPar['Optimizer']['Par'][1])
            par3 = float(self.dicPar['Optimizer']['Par'][2])
            par4 = int(self.dicPar['Optimizer']['Par'][3])

            if int(self.dicPar['Optimizer']['Par'][4]) == 0:
                par5 = self.reg_method.Never
            elif int(self.dicPar['Optimizer']['Par'][4]) == 1:
                par5 = self.reg_method.Once
            elif int(self.dicPar['Optimizer']['Par'][4]) == 2:
                par5 = self.reg_method.EachIteration

            par6 = int(self.dicPar['Optimizer']['Par'][5])
            self.reg_method.SetOptimizerAsGradientDescent(par1, par2, par3, par4, par5, par6)

        elif self.dicPar['Optimizer']['Method'] == "Gradient Descent Line Search":

            par1 = float(self.dicPar['Optimizer']['Par'][0])
            par2 = int(self.dicPar['Optimizer']['Par'][1])
            par3 = float(self.dicPar['Optimizer']['Par'][2])
            par4 = int(self.dicPar['Optimizer']['Par'][3])
            par5 = float(self.dicPar['Optimizer']['Par'][4])
            par6 = float(self.dicPar['Optimizer']['Par'][5])
            par7 = float(self.dicPar['Optimizer']['Par'][6])
            par8 = int(self.dicPar['Optimizer']['Par'][7])
            if int(self.dicPar['Optimizer']['Par'][8]) == 0:
                par9 = self.reg_method.Never
            elif int(self.dicPar['Optimizer']['Par'][8]) == 1:
                par9 = self.reg_method.Once
            elif int(self.dicPar['Optimizer']['Par'][8]) == 2:
                par9 = self.reg_method.EachIteration

            par10 = int(self.dicPar['Optimizer']['Par'][9])

            self.reg_method.SetOptimizerAsGradientDescentLineSearch(par1, par2, par3, par4, par5, par6, par7, par8,
                                                                    par9, par10)

        elif self.dicPar['Optimizer']['Method'] == "Conjugate Gradient Line Search":

            par1 = float(self.dicPar['Optimizer']['Par'][0])
            par2 = int(self.dicPar['Optimizer']['Par'][1])
            par3 = float(self.dicPar['Optimizer']['Par'][2])
            par4 = int(self.dicPar['Optimizer']['Par'][3])
            par5 = float(self.dicPar['Optimizer']['Par'][4])
            par6 = float(self.dicPar['Optimizer']['Par'][5])
            par7 = float(self.dicPar['Optimizer']['Par'][6])
            par8 = int(self.dicPar['Optimizer']['Par'][7])
            if int(self.dicPar['Optimizer']['Par'][8]) == 0:
                par9 = self.reg_method.Never
            elif int(self.dicPar['Optimizer']['Par'][8]) == 1:
                par9 = self.reg_method.Once
            elif int(self.dicPar['Optimizer']['Par'][8]) == 2:
                par9 = self.reg_method.EachIteration

            par10 = int(self.dicPar['Optimizer']['Par'][9])
            self.reg_method.SetOptimizerAsConjugateGradientLineSearch(par1, par2, par3, par4, par5, par6, par7, par8,
                                                                      par9, par10)

        elif self.dicPar['Optimizer']['Method'] == "Exhaustive":
            par1 = int(self.dicPar['Optimizer']['Par'][1])
            par2 = int(self.dicPar['Optimizer']['Par'][2])
            par3 = int(self.dicPar['Optimizer']['Par'][3])
            par4 = int(self.dicPar['Optimizer']['Par'][4])
            par5 = int(self.dicPar['Optimizer']['Par'][5])
            par6 = int(self.dicPar['Optimizer']['Par'][6])
            par13 = float(self.dicPar['Optimizer']['Par'][0])
            vect1 = [par1, par2, par3, par4, par5, par6]

            self.reg_method.SetOptimizerAsExhaustive(vect1, par13)

        elif self.dicPar['Optimizer']['Method'] == "LBFGSB":
            par1 = float(self.dicPar['Optimizer']['Par'][0])
            par2 = int(self.dicPar['Optimizer']['Par'][1])
            par3 = int(self.dicPar['Optimizer']['Par'][2])
            par4 = int(self.dicPar['Optimizer']['Par'][3])
            par5 = float(self.dicPar['Optimizer']['Par'][4])

            self.reg_method.SetOptimizerAsLBFGSB(par1, par2, par3, par4, par5)
        elif self.dicPar['Optimizer']['Method'] == "Powell":
            par1 = int(self.dicPar['Optimizer']['Par'][0])
            par2 = int(self.dicPar['Optimizer']['Par'][1])
            par3 = float(self.dicPar['Optimizer']['Par'][2])
            par4 = float(self.dicPar['Optimizer']['Par'][3])
            par5 = float(self.dicPar['Optimizer']['Par'][4])
            self.reg_method.SetOptimizerAsPowell(par1, par2, par3, par4, par5)

        elif self.dicPar['Optimizer']['Method'] == "Amoeba":
            par1 = float(self.dicPar['Optimizer']['Par'][0])
            par2 = int(self.dicPar['Optimizer']['Par'][1])
            par3 = float(self.dicPar['Optimizer']['Par'][2])
            par4 = float(self.dicPar['Optimizer']['Par'][3])
            self.reg_method.SetOptimizerAsAmoeba(par1, par2, par3, par4)

        if self.dicPar['Optimizer']['Method'] != "Exhaustive" or self.dicPar['Optimizer']['Method'] != "LBFGSB":

            if self.dicPar['Optimizer']['MethodScaling'] == "Physical Shift":

                par1 = int(self.dicPar['Optimizer']['ScalePar'][0])
                par2 = float(self.dicPar['Optimizer']['ScalePar'][1])
                self.reg_method.SetOptimizerScalesFromPhysicalShift(par1, par2)

            elif self.dicPar['Optimizer']['MethodScaling'] == "Jacobian":
                par1 = int(self.dicPar['Optimizer']['ScalePar'][0])
                self.reg_method.SetOptimizerScalesFromJacobian(par1)

            elif self.dicPar['Optimizer']['MethodScaling'] == "Index Shift":

                par1 = int(self.dicPar['Optimizer']['ScalePar'][0])
                par2 = float(self.dicPar['Optimizer']['ScalePar'][1])
                self.reg_method.SetOptimizerScalesFromIndexShift(par1, par2)
        elif self.dicPar['Optimizer']['Method'] != "Exhaustive":

            par7 = float(self.dicPar['Optimizer']['Par'][7])
            par8 = float(self.dicPar['Optimizer']['Par'][8])
            par9 = float(self.dicPar['Optimizer']['Par'][9])
            par10 = float(self.dicPar['Optimizer']['Par'][10])
            par11 = float(self.dicPar['Optimizer']['Par'][11])
            par12 = float(self.dicPar['Optimizer']['Par'][12])

            vect2 = [par7, par8, par9, par10, par11, par12]

            self.reg_method.SetOptimizerScales(vect2)

    def initInterpolator(self):

        if self.dicPar['Interpolator'] == "Nearest neighbor":
            self.interpolator = sitk.sitkNearestNeighbor
        elif self.dicPar['Interpolator'] == "Linear Interpolation":
            self.interpolator = sitk.sitkLinear
        elif self.dicPar['Interpolator'] == "BSpline":
            self.interpolator = sitk.sitkBSpline
        elif self.dicPar['Interpolator'] == "Gaussian":
            self.interpolator = sitk.sitkGaussian
        elif self.dicPar['Interpolator'] == "Label Gaussian":
            self.interpolator = sitk.sitkLabelGaussian
        elif self.dicPar['Interpolator'] == "Hamming Windowed Sinc":
            self.interpolator = sitk.sitkHammingWindowedSinc
        elif self.dicPar['Interpolator'] == "Cosine Windowed Sinc":
            self.interpolator = sitk.sitkCosineWindowedSinc
        elif self.dicPar['Interpolator'] == "Welch Windowed Sinc":
            self.interpolator = sitk.sitkWelchWindowedSinc
        elif self.dicPar['Interpolator'] == "Lanczos Windowed Sinc":
            self.interpolator = sitk.sitkLanczosWindowedSinc
        elif self.dicPar['Interpolator'] == "Blackman Windowed Sinc":
            self.interpolator = sitk.sitkBlackmanWindowedSinc

        self.reg_method.SetInterpolator(self.interpolator)

    def initScaling(self):

        vect1 = []
        vect2 = []

        for i in range(0, int(len(self.dicPar['Scaling']))):
            parS = int(self.dicPar['Scaling'][i])
            parSm = float(self.dicPar['Scaling'][i])
            vect1.append(parS)
            vect2.append(parSm)

        self.reg_method.SetShrinkFactorsPerLevel(vect1)
        self.reg_method.SetSmoothingSigmasPerLevel(vect2)

        self.reg_method.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()

    def Execute(self):
        print(self.reg_method)
        self.Final_Transform = self.reg_method.Execute(self.ImageFixe, self.ImageMoving)
        print('Done Executing')

    def computeJacobian(self, vectorFieldITK):

        filterJacob = sitk.DisplacementFieldJacobianDeterminantFilter()
        return filterJacob.Execute(vectorFieldITK)

    def ApplyTransform(self, ImageIn, FlagRigid):

        ImageITK = imageFromNumpyToITK(ImageIn)

        if FlagRigid:
            ImageITK = sitk.Resample(ImageITK, self.ImageFixe, self.init_t, self.interpolator, 0.0,
                                     ImageITK.GetPixelIDValue())

        ImageOut = sitk.Resample(ImageITK, self.ImageFixe, self.interpolator, 0.0, ImageITK.GetPixelIDValue())

        return np.copy(imageFromITKToNumpy(ImageOut))

    def ApplyMovingTransform(self, central_indexes):
        moving_transformed = sitk.Resample(self.ImageMoving, self.ImageFixe, self.initial_transform, self.interpolator,
                                           0.0, self.ImageMoving.GetPixelIDValue())

        alpha = 0.5
        combined = [(1.0 - alpha) * self.ImageFixe[:, :, central_indexes[2]] + \
                    alpha * moving_transformed[:, :, central_indexes[2]],
                    (1.0 - alpha) * self.ImageFixe[:, central_indexes[1], :] + \
                    alpha * moving_transformed[:, central_indexes[1], :],
                    (1.0 - alpha) * self.ImageFixe[central_indexes[0], :, :] + \
                    alpha * moving_transformed[central_indexes[0], :, :]]

        combined_isotropic = []

        for img in combined:
            original_spacing = img.GetSpacing()
            original_size = img.GetSize()

            min_spacing = min(original_spacing)
            new_spacing = [min_spacing, min_spacing]
            new_size = [int(round(original_size[0] * (original_spacing[0] / min_spacing))),
                        int(round(original_size[1] * (original_spacing[1] / min_spacing)))]
            resampled_img = sitk.Resample(img, new_size, sitk.Transform(),
                                          sitk.sitkLinear, img.GetOrigin(),
                                          new_spacing, img.GetDirection(), 0.0,
                                          img.GetPixelIDValue())
            combined_isotropic.append(imageFromITKToNumpy(resampled_img))
        return combined_isotropic

    def returnNumpyImage(self):
        print('Returning')
        self.ImageMovingBef = imageFromITKToNumpy(self.ImageMoving)
        self.ImageFixedBef = imageFromITKToNumpy(self.ImageFixe)
        print('Transforming Moving')
        self.ImageMoving = sitk.Resample(self.ImageMoving, self.ImageFixe, self.Final_Transform, self.interpolator, 0.0,
                                         self.ImageMoving.GetPixelIDValue())
        self.ImageMoving
        ImageOut = imageFromITKToNumpy(self.ImageMoving)
        print('Chess Image')
        self.chessImage = self.giveChessImage(self.ImageFixedBef,ImageOut,10)
        print('Transform Field Displacement ')
        FilterTransform = sitk.TransformToDisplacementFieldFilter()
        FilterTransform.SetReferenceImage(self.ImageFixe)
        self.displacementField = FilterTransform.Execute(self.Final_Transform)
        print("Jacob")
        self.transformOut = imageFromITKToNumpy(self.displacementField)
        vectorJacob = self.computeJacobian(self.displacementField)

        self.vectorFieldJacobian = imageFromITKToNumpy(vectorJacob)

        return ImageOut

    def giveChessImage(self, Im1, Im2, BlocSpeed):
        SizeZVol = Im1.shape[0]
        SizeXVol = Im1.shape[1]
        SizeYVol = Im1.shape[2]

        iterx = 0
        itery = 0
        iterz = 0

        chessMap = np.zeros((SizeZVol, SizeXVol, SizeYVol))

        for xRef in np.arange(0, SizeXVol - 1, BlocSpeed):
            itery = 0
            iterx += 1
            for yRef in np.arange(0, SizeYVol - 1, BlocSpeed):
                iterz = 0
                itery += 1
                for zRef in np.arange(0, SizeZVol - 1, BlocSpeed):
                    iterz += 1

                    xMinRef = xRef - int(BlocSpeed / 2)
                    yMinRef = yRef - int(BlocSpeed / 2)
                    zMinRef = zRef - int(BlocSpeed / 2)

                    xMaxRef = xRef + int(BlocSpeed / 2)
                    yMaxRef = yRef + int(BlocSpeed / 2)
                    zMaxRef = zRef + int(BlocSpeed / 2)

                    if xMinRef < 0:
                        xMinRef = 0
                    if yMinRef < 0:
                        yMinRef = 0
                    if zMinRef < 0:
                        zMinRef = 0

                    if xMaxRef >= SizeXVol:
                        xMaxRef = SizeXVol - 1
                    if yMaxRef >= SizeYVol:
                        yMaxRef = SizeYVol - 1
                    if zMaxRef >= SizeZVol:
                        zMaxRef = SizeZVol - 1

                    if ((iterz + itery + iterx) % 2) == 0:
                        chessMap[zMinRef:zMaxRef, xMinRef:xMaxRef, yMinRef:yMaxRef] = Im1[zMinRef:zMaxRef,
                                                                                      xMinRef:xMaxRef,
                                                                                      yMinRef:yMaxRef]
                    else:
                        chessMap[zMinRef:zMaxRef, xMinRef:xMaxRef, yMinRef:yMaxRef] = Im2[zMinRef:zMaxRef,
                                                                                      xMinRef:xMaxRef,
                                                                                      yMinRef:yMaxRef]

        return chessMap