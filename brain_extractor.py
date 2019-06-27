from populse_mia.pipeline_manager.process_mia import ProcessMIA
import traits.api as traits
from traits.api import CArray
import nibabel as nib
import os
import numpy as np
from deepbrain import Extractor
import shutil

class ClinicBrainExtractor(ProcessMIA):
    """
    Extract brain from T2 image based on deep learning algorithm from deepbrain library:
    Brain image processing tools using Deep Learning focused on speed and accuracy.

    Take has input a numpy array and his attached json as well as the probability threathold
    """

    def __init__(self):
        super(ClinicBrainExtractor, self).__init__()

        # Inputs description
        array_desc = '3D Input Array'
        jason_file_desc = 'Path to the Nifti Header Jason file'

        # Ouputs description
        file_desc = 'Brain Mask'
        out_prefix_descr = "Prefix à Rajouter au fichier nii"

        # Inputs traits
        trait_array = CArray(output=False, optional=False, desc=array_desc)
        self.add_trait("array_in",trait_array)
        self.add_trait("nifti_jason_header_in",traits.File(output=False,optional=False,desc=jason_file_desc))
        self.add_trait("probability_treathold", traits.List(traits.Float(), [0.5], output=False, optional=True, desc="Probability Threathold"))
        # Outputs traits
        trait_array = CArray(output=True, optional=False, desc=array_desc)
        self.add_trait("array_out",trait_array)
        self.add_trait("nifti_jason_header_out", traits.File(output=True, optional=False, desc=jason_file_desc))




    def list_outputs(self):
        super(ClinicBrainExtractor  , self).list_outputs()
        # Generating the filename by hand

        if not self.nifti_jason_header_in:
            print('"in_file" plug is mandatory for Convert process')
            return {}
        else:
            path, filename = os.path.split(self.nifti_jason_header_in)
            out_filename = 'M_' + filename
            output_dict = {'nifti_jason_header_out': os.path.join(path, out_filename)}

        inheritance_dict =  {output_dict['nifti_jason_header_out']: self.nifti_jason_header_in}

        return output_dict, inheritance_dict


    def _run_process(self):


            path, filename = os.path.split(self.nifti_jason_header_in)
            shutil.copy(self.nifti_jason_header_in, path + 'tmp.json' )
            shutil.move(path + 'tmp.json',self.nifti_jason_header_out)


            ext = Extractor()
            print(ext)
            # `prob` will be a 3d numpy image containing probability
            # of being brain tissue for each of the voxels in `img`
            self.array_out = ext.run(self.array_in)
            print(self.array_out)


if __name__ == "__main__":

    path_file = ''
    input_image = nib.load(path_file)  # Loading the nibabel image
    array_out = np.array(input_image.get_data())
    ext = Extractor()
    prob = ext.run(array_out)
