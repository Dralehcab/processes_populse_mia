import os
import nibabel as nib
import json
import numpy as np
import re

class NiftiHeaderManagement():
    """
    Class to save nibabel Nifti 1 header as Jason file and load them back
    """

    def __init__(self,path_jason='', nib_header=None):

        if path_jason != '':
            filename, file_extension = os.path.splitext(path_jason)

            if os.path.isfile(path_jason) and (file_extension in ['.JSON', '.json']):
                self.path_jason = path_jason
            else:
                print('Unrecognized Jason File')
        else:
            self.path_jason = ''

        if isinstance(nib_header,nib.nifti1.Nifti1Header):
            self.nib_header = nib_header
        else:
            self.nib_header = None

    def set_path_jason(self,path_jason):

        filename, file_extension = os.path.splitext(path_jason)

        if os.path.exists(os.path.dirname(path_jason)) and (file_extension in ['.JSON', '.json']):
            self.path_jason = path_jason
        else:
            print('Unrecognized Jason File')

    def set_nib_header(self,nib_header):

        if isinstance(nib_header,nib.nifti1.Nifti1Header):
            self.nib_header = nib_header
        else:
            print('Argument is not a valid nibabel Nifti 1 Header')

    def save_header_to_jason(self):

        dic = {}

        for field in self.nib_header:

            if "bytes" in self.nib_header[field].dtype.name:
                dic[field] = re.findall(r"'([^']*)'",str(self.nib_header[field].item()))[0]

            elif self.nib_header[field].size == 1:
                dic[field] = self.nib_header[field].item()

            else:
                dic[field] = self.nib_header[field].tolist()

        with open(self.path_jason, 'w+') as fp:
            json.dump(dic, fp)
        fp.close()

    def load_jason_to_header(self):

        with open(self.path_jason) as f:
            dic = json.load(f)

        f.close()

        self.nib_header = nib.Nifti1Header()

        for field in self.nib_header:
            if field in dic:
                self.nib_header[field] = dic[field]

        return self.nib_header,[self.nib_header["srow_x"],self.nib_header["srow_y"],self.nib_header["srow_z"],[0,0,0,1]]

if __name__ == '__main__':
    path_nifti = "/Data/MIA_Data/Test_Project/Test1/data/raw_data" \
                 "/2018_06_11_Anat_F98_J2-2018_06_11_Anat_F98_J2-2018-06"\
                 "-11_13-58-56-10-T2_TurboRARE-Bruker-RARE-00-02-40.000.nii"

    path_jason = "./test.json"

    input_image = nib.load(path_nifti)  # Loading the nibabel image
    array_in = np.array(input_image.get_data())
    input_image_header = input_image.header
    nifti = NiftiHeaderManagement()
    nifti.set_nib_header(input_image_header)
    nifti.set_path_jason(path_jason)
    nifti.save_header_to_jason()

    nifti2 = NiftiHeaderManagement()
    nifti2.set_path_jason(path_jason)
    jason_header, affine = nifti2.load_jason_to_header()

    nifti_image = nib.Nifti1Image(array_in, affine, jason_header)

    nib.save(nifti_image, './test.nii')

