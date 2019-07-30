import os
import pandas as pd
from __init__ import fslDir
from PreMelodicProcessing import Preprocessing


class PostMelodic(Preprocessing):

    def __init__(self, Preprocessing):

        self.subjectID = Preprocessing.subjectID
        self.path_fmri = Preprocessing.path_fmri
        self.path_HCP = Preprocessing.path_HCP

    def denoise(self):

        if os.path.exists(self.path_fmri + "/denoise.ica/filtered_func_data.ica/HandDenoisedLabels.txt"):

            with open(self.path_fmri + "/denoise.ica/filtered_func_data.ica/HandDenoisedLabels.txt", "r") as noise_file:
                for line in noise_file:
                    pass
                raw_noise = line
            noise = raw_noise.replace(' ','').replace('[','').replace(']','')

            os.system(
                fslDir + "fsl_regfilt -i " + self.path_fmri + "/denoise.ica/filtered_func_data_smo.nii.gz -o " +
                self.path_fmri + "/denoise.ica/Denoised_data.nii.gz -d " +
                self.path_fmri + "/denoise.ica/filtered_func_data.ica/melodic_mix -f " + noise
            )


    def mask_mean_time_series(self):

        if not os.path.isdir(self.path_fmri + "/meants"):
            os.mkdir(self.path_fmri + "/meants")

        mask_types = ["WM", "GM", "CSF"]
        for mask in mask_types:

            os.system(
                fslDir + "fslmeants -i " + self.path_fmri + "/denoise.ica/Denoised_data.nii.gz -o " +
                self.path_fmri + "meants/meants" + mask + ".csv -m " +
                self.path_HCP + "/" + mask + "mask_bin_2.00.nii.gz"
            )


    def create_all_confounds(self):

        csf = pd.read_csv(self.path_fmri + '/meants/meantsCSF.csv', sep=',', header=None)
        wm = pd.read_csv(self.path_fmri + '/meants/meantsWM.csv', sep=',', header=None)
        mc = pd.read_csv(self.path_fmri + '/mc/prefiltered_func_data_mcf.par', sep='  ', header=None)
        
        if csf[0].count() == wm[0].count() == mc[0].count():
            pass
        else:
            print("{}: Not the same number of rows".format(self.subjectID))

        if not os.path.isdir(self.path_fmri + "/spreadsheets"):
            os.mkdir(self.path_fmri + "/spreadsheets")
        all_confounds = pd.concat((csf, wm, mc), axis=1)
        all_confounds.to_csv(self.path_fmri + '/spreadsheets/all_confounds.csv', sep=',', header=False, index=False)
