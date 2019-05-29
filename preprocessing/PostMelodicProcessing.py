import os
import subprocess
from shutil import copyfile, copytree
from __init__ import fslDir
from PreMelodicProcessing import Preprocessing


class PostMelodic(Preprocessing):

    def __init__(self, Preprocessing):

        self.subjectID = Preprocessing.subjectID
        self.path_fmri = Preprocessing.path_fmri
        self.path_HCP = Preprocessing.path_HCP

    def denoise(self):

        with open(self.path_fmri + "/denoise.ica/filtered_func_data.ica/HandDenoisedLabels.txt", "r") as noise_file:
            for line in noise_file:
                pass
            raw_noise = line
        raw_noise = raw_noise[0][1:-1]

        noise = ''
        for character in raw_noise:
            if character != ' ':
                noise += character

        os.system(
            fslDir + "fsl_regfilt -i self.path_fmri/denoise.ica/filtered_func_data_smo.nii.gz -o " +
            self.path_fmri + "/denoise.ica/Denoised_data.nii.gz -d " +
            self.path_fmri + "/denoise.ica/filtered_func_data.ica/melodic_mix -f " + noise + " -v"
        )