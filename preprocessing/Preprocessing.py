import os
from shutil import copyfile
from __init__ import fslDir


class Preprocessing:

    def __init__(self, subjectID):
        self.subjectID = subjectID
        self.path_fmri = "/shared/studies/nonregulated/connectome/fmri/subjects/" + subjectID
        self.path_HCP = "/shared/studies/nonregulated/connectome/Subjects/" + subjectID + "/T1w/"


    def remove_first_two_volumes(self):
        try:
            os.system(
                fslDir + "fslroi " + self.path_fmri + "/rawfunc.nii.gz " +
                self.path_fmri + "/prefiltered_func_data_2cut 2 238"
            )
        except:
            print("{}: Error removing first two volumes from time series".format(self.subjectID))


    def slicetime_correction(self):
        try:
            os.system(
                fslDir + "slicetimer -i " + self.path_fmri + "/prefiltered_func_data_2cut -o " +
                self.path_fmri + "/prefiltered_func_data_st -r 2.5 --odd"
            )
        except:
            print("{}: Error performing slicetime correction".format(self.subjectID))


    def motion_correction(self):
        try:
            os.mkdir(os.path.join(self.path_fmri, "mc"))
            os.system(
                fslDir + "mcflirt -in " + self.path_fmri + "/prefiltered_func_data_2cut.nii.gz" +
                " -out " + self.path_fmri + "/mc/prefiltered_func_data_mcf -plots -spline_final -mats -rmsrel -rmsabs"
            )
            copyfile(os.path.join(self.path_fmri, "mc/prefiltered_func_data_mcf.nii.gz"),
                     os.path.join(self.path_fmri, "prefiltered_func_data_mcf.nii.gz"))
        except:
            print("{}: Error performing motion correction".format(self.subjectID))


    def intensity_normalization(self):
        try:
            os.system(
                fslDir + "fslmaths " + self.path_fmri + "prefiltered_func_data_mcf.nii.gz -ing 10000 " +
                self.path_fmri + "/prefiltered_func_data_in -odt float"
            )
        except:
            print("{}: Error performing intensity normalization".format(self.subjectID))


    def temporal_mean(self):
        try:
            os.system(
                fslDir + "fslmaths " + self.path_fmri + "/prefiltered_func_data_in.nii.gz -Tmean " +
                self.path_fmri + "/tempMean"
            )
        except:
            print("{}: Error calculating temporal mean".format(self.subjectID))


    def temporal_filtering(self):
        try:
            os.system(
                fslDir + "fslmaths " + self.path_fmri + "/prefiltered_func_data_in.nii.gz -bptf 400 -1 -add " +
                self.path_fmri + "tempMean.nii.gz " + self.path_fmri + "/filtered_func_data"
            )
        except:
            print("{}: Error performing temporal filtering with 2000s cutoff".format(self.subjectID))


    def brain_extraction(self):
        try:
            os.system(
                fslDir + "fslmaths " + self.path_fmri + "/filtered_func_data.nii.gz -Tmean " +
                self.path_fmri + "/mean_func_filtered"
            )
            os.system(
                fslDir + "bet2 " + self.path_fmri + "/mean_func_filtered " +
                self.path_fmri + "filtered_mask -f 0.3 -n -m"
            )
            os.system(
                fslDir + "immv " + self.path_fmri + "/filtered_mask_mask " + self.path_fmri + "/filtered_mask"
            )
            os.system(
                fslDir + "fslmaths " + self.path_fmri + "/filtered_func_data.nii.gz -mas " +
                self.path_fmri + "/filtered_mask " + self.path_fmri + "/filtered_func_data_bet.nii.gz"
            )

            os.system(
                fslDir + "fslmaths " + self.path_fmri + "/magnitude_combined.nii.gz -Tmean " +
                self.path_fmri + "/mean_magnitude_combined"
            )
            os.system(
                fslDir + "bet2 " + self.path_fmri + "/mean_magnitude_combined" +
                self.path_fmri + "/magnitude_mask -f 0.3 -n -m"
            )
            os.system(
                fslDir + "immv " + self.path_fmri + "/magnitude_mask_mask " + self.path_fmri + "/magnitude_mask"
            )
            os.system(
                fslDir + "fslmaths " + self.path_fmri + "/magnitude_combined.nii.gz -mas " +
                self.path_fmri + "magnitude_mask " + self.path_fmri + "/mag_brain.nii.gz"
            )
        except:
            print("{}: Error extracting brain".format(self.subjectID))


    def
