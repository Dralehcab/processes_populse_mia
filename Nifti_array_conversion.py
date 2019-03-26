from populse_mia.pipeline_manager.process_mia import ProcessMIA
import traits.api as traits
from traits.api import CArray
import nibabel as nib
import os
import numpy as np
import sys

sys.path.append('/home/broche/Code/Python/processes_populse_mia/utils')
from NiftiHeaderManagement import NiftiHeaderManagement


class NiftiToArray(ProcessMIA):
    """
    Convert à Nifti File to Numpy array
    Input: Path of the Nifti File
    Output: Image Data as Numpy Array
            Path to Json File Containing the Image Nifti Header
    """

    def __init__(self):
        super(NiftiToArray, self).__init__()

        # Inputs description
        file_desc = '3D Input Nifti file'
        out_prefix_descr = "Prefix à Rajouter au fichier Jason"

        # Outputs description
        array_desc = '3D Output Array'
        jason_file_desc = 'Path to the Nifti Header Jason file'

        # Inputs traits
        self.add_trait("file_image_in",traits.File(output=False,desc=file_desc))
        self.add_trait("out_prefix", traits.String('c', output=False, optional=True, desc=out_prefix_descr))

        # Outputs traits
        trait_array = CArray(output=True, optional=False, desc=array_desc)
        self.add_trait("array_out",trait_array)
        self.add_trait("nifti_jason_header_out",traits.File(output=True,desc=jason_file_desc))

    def list_outputs(self):
        super(NiftiToArray, self).list_outputs()

        # Generating the filename by hand
        if not self.file_image_in:
            print('"in_file" plug is mandatory for Convert process')
            return {}
        else:
            path, filename = os.path.split(self.file_image_in)
            out_filename = self.out_prefix + filename
            out_filename = os.path.splitext(out_filename)[0] + '.json'
            output_dict = {'nifti_jason_header_out': os.path.join(path, out_filename)}

        # Generating the inheritance dictionary

        inheritance_dict = {output_dict['nifti_jason_header_out']: self.file_image_in}

        return output_dict, inheritance_dict

    def _run_process(self):

        if not self.file_image_in:
            print('"in_file" plug is mandatory for a Conversion Process')
            return
        else:
            input_image = nib.load(self.file_image_in)  # Loading the nibabel image
            self.array_out = np.array(input_image.get_data())# Getting the 3D volume as a numpy array
            image_header = input_image.header

            jason_header = NiftiHeaderManagement()
            jason_header.set_nib_header(image_header)

            path, filename = os.path.split(self.file_image_in)
            out_filename = self.out_prefix + filename
            out_filename = os.path.splitext(out_filename)[0] + '.json'

            jason_header.set_path_jason( os.path.join(path, out_filename))
            jason_header.save_header_to_jason()


class ArrayToNifti(ProcessMIA):
    """
    Convert a Numpy Array and a Jason header file into a Nifti file
    """

    def __init__(self):
        super(ArrayToNifti, self).__init__()

        # Inputs description
        array_desc = '3D Input Array'
        jason_file_desc = 'Path to the Nifti Header Jason file'

        # Ouputs description
        file_desc = '3D Ouput Nifti file'

        # Inputs traits
        trait_array = CArray(output=False, optional=False, desc=array_desc)
        self.add_trait("array_in",trait_array)
        self.add_trait("nifti_jason_header_in",traits.File(output=False,optional=False,desc=jason_file_desc))

        # Outputs traits
        self.add_trait("file_image_out",traits.File(output=True, desc=file_desc))

    def list_outputs(self):
        super( ArrayToNifti, self).list_outputs()

        # Generating the filename by hand
        if not self.nifti_jason_header_in:
            print('"Nifti Jason Header" plug is mandatory for Convert process')
            return {}
        else:
            out_filename = os.path.splitext(self.nifti_jason_header_in)[0] + '.nii'

            print(out_filename)
            output_dict = {'file_image_out': out_filename}

        # Generating the inheritance dictionary
        inheritance_dict = {output_dict['file_image_out']: self.nifti_jason_header_in}

        return output_dict, inheritance_dict


    def _run_process(self):
        if not self.nifti_jason_header_in:
            print('"Nifti Header Jason" plug is mandatory for a Conversion Process')
            return
        else:

            jason_header = NiftiHeaderManagement()
            jason_header.set_path_jason(self.nifti_jason_header_in)
            header, affine = jason_header.load_jason_to_header()

            nifti_image = nib.Nifti1Image(self.array_in, affine, header)
            nib.save(nifti_image,os.path.splitext(self.nifti_jason_header_in)[0] + '.nii')


