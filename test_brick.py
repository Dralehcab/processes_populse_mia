import os
import traits.api as traits  # used to declare the inputs/outputs of the process
from traits.api import Array, HasTraits, NO_COMPARE
import nibabel as nib  # used to read and save Nifti images
from nipype.interfaces import spm  # used to use SPM's Smooth
from scipy.ndimage.filters import gaussian_filter  # used to apply the smoothing on an array
from populse_mia.pipeline_manager.process_mia import ProcessMIA  # base class that the created process has to inherit from

class Array(HasTraits):
    x = Array(comparison_mode=NO_COMPARE)

    def _x_changed(self):
        print('Array Changed')


class File_To_Array(ProcessMIA):
    """
-  Files_To_List (mia_processes.tools.tools.Files_To_List)
*** From 2 file names, generating a list containing all theses file names ***
    '/home/ArthurBlair/data/raw_data/Anat.nii ' + '/home/ArthurBlair/data/raw_data/Func.nii' -> Files_To_List ->
    ['/home/ArthurBlair/data/raw_data/Anat.nii', '/home/ArthurBlair/data/raw_data/Func.nii']
    * Input parameters:
        * file1: a string corresponding to an existing path file (traits.File)
            <ex. /home/ArthurBlair/data/raw_data/Anat.nii>
        * file2: a string corresponding to an existing path file (traits.File)
            <ex. /home/ArthurBlair/data/raw_data/Func.nii>
    * Output parameters:
        * file_list: a list (traits.List)
            <ex. ['/home/ArthurBlair/data/raw_data/Anat.nii',
                 '/home/ArthurBlair/data/Func.nii']>
    """

    def __init__(self):
        super(File_To_Array, self).__init__()

        # Inputs description
        file_desc = '3D input file'

        # Outputs description
        array_desc = '3D Output Array'

        # Inputs traits
        self.add_trait("file_image",traits.File(output=False,desc=file_desc))
        # Outputs traits
        trait_array = Array(output=True,optional=False,desc=array_desc)
        trait_array._metadata = {'output': True, 'optional': False,'desc': 'Metadata'}
        trait_array.output = True
        trait_array.optional = False


        self.add_trait("output_array",trait_array)

        self.add_trait("file_list",traits.List(output=False,desc='T'))

    def list_outputs(self):
        super(File_To_Array, self).list_outputs()
        return {'output_array': []}, {}


    def run_process_mia(self):
        print('Test')








class SmoothSpmScipy(ProcessMIA):

    def __init__(self):
        super(SmoothSpmScipy, self).__init__()

        # Inputs
        self.add_trait("in_file", traits.File(output=False, desc='3D input file'))  # Mandatory plug

        # For inputs/outputs that are lists, it is possible to specify which the type of the list element (here
        # traits.Float(). The second value ([1.0, 1.0, 1.0]) corresponds to the default value
        self.add_trait("fwhm", traits.List(traits.Float(), [1.0, 1.0, 1.0], output=False, optional=True,
                                           desc='List of fwhm for each dimension (in mm)'))
        self.add_trait("out_prefix", traits.String('s', output=False, optional=True, desc='Output file prefix'))
        self.add_trait("method", traits.Enum('SPM', 'Scipy', output=False, optional=True,
                                             desc='Method used (either "SPM" or "Scipy")'))

        # Output
        self.add_trait("smoothed_file", traits.File(output=True, desc='Output file'))  # Mandatory plug

        self.process = spm.Smooth()

    def list_outputs(self):
        # Depending on the chosen method, the output dictionary will be generated differently
        if self.method in ['SPM', 'Scipy']:
            if self.method == 'SPM':
                # Nipype interfaces have already a _list_outputs method that generates the output dictionary
                if not self.in_file:
                    print('"in_file" plug is mandatory for a Smooth process')
                    return {}
                else:
                    self.process.inputs.in_files = self.in_file  # The input for a SPM Smooth is "in_files"
                self.process.inputs.out_prefix = self.out_prefix
                nipype_dict = self.process._list_outputs()  # Generates: {'smoothed_files' : [out_filename]}
                output_dict = {'smoothed_file': nipype_dict['smoothed_files'][0]}
            else:
                # Generating the filename by hand
                if not self.in_file:
                    print('"in_file" plug is mandatory for a Smooth process')
                    return {}
                else:
                    path, filename = os.path.split(self.in_file)
                    out_filename = self.out_prefix + filename
                    output_dict = {'smoothed_file': os.path.join(path, out_filename)}

            # Generating the inheritance dictionary
            inheritance_dict = {output_dict['smoothed_file']: self.in_file}

            return output_dict, inheritance_dict

        else:
            print('"method" input has to be "SPM" or "Scipy" for a Smooth process')
            return {}

    def _run_process(self):
        # Depending on the chosen method, the output file will be generated differently
        if self.method in ['SPM', 'Scipy']:
            if self.method == 'SPM':
                # Make sure to call the manage_matlab_launch_parameters method to set the config parameters
                self.manage_matlab_launch_parameters()
                if not self.in_file:
                    print('"in_file" plug is mandatory for a Smooth process')
                    return
                else:
                    self.process.inputs.in_files = self.in_file  # The input for a SPM Smooth is "in_files"
                self.process.inputs.fwhm = self.fwhm
                self.process.inputs.out_prefix = self.out_prefix

                self.process.run()  # Running the interface

            else:
                if not self.in_file:
                    print('"in_file" plug is mandatory for a Smooth process')
                    return
                else:
                    input_image = nib.load(self.in_file)  # Loading the nibabel image
                    input_image_header = input_image.header
                    input_array = input_image.get_data()  # Getting the 3D volume as a numpy array

                    # Getting the image resolution in x, y and z
                    x_resolution = abs(input_image_header['pixdim'][1])
                    y_resolution = abs(input_image_header['pixdim'][2])
                    z_resolution = abs(input_image_header['pixdim'][3])

                    # Convert the fwhm for each dimension from mm to pixel
                    x_fwhm = self.fwhm[0] / x_resolution
                    y_fwhm = self.fwhm[1] / y_resolution
                    z_fwhm = self.fwhm[2] / z_resolution
                    pixel_fwhm = [x_fwhm, y_fwhm, z_fwhm]

                    sigma = [pixel_fwhm_dim / 2.355 for pixel_fwhm_dim in pixel_fwhm]  # Converting fwmh to sigma
                    output_array = gaussian_filter(input_array, sigma)  # Filtering the array

                    # Creating a new Nifti image with the affine/header of the input_image
                    output_image = nib.Nifti1Image(output_array, input_image.affine, input_image.header)

                    # Saving the image
                    path, filename = os.path.split(self.in_file)
                    out_filename = self.out_prefix + filename
                    nib.save(output_image, os.path.join(path, out_filename))

        else:
            print('"method" input has to be "SPM" or "Scipy" for a Smooth process')
            return {}