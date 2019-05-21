import os
import subprocess
from shutil import copyfile
from __init__ import fslDir


class Preprocessing:

    def __init__(self, subjectID):
        self.subjectID = subjectID
        self.path_fmri = "/shared/studies/nonregulated/connectome/fmri/subjects/" + subjectID + "/"
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

            os.mkdir(os.path.join(self.path_fmri, "dc"))
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
                self.path_fmri + "/magnitude_mask " + self.path_fmri + "/dc/mag_brain.nii.gz"
            )
        except:
            print("{}: Error extracting brain".format(self.subjectID))


    # Should really consider breaking this up at some point
    def epi_distortion_correction(self):
        try:
            os.system(
                fslDir + "fslmaths " + self.path_fmri + "/filtered_func_data_bet.nii.gz -Tmean " +
                self.path_fmri + "/dc/mean_filtered_func_data_bet.nii.gz"
            )

            os.system(
                fslDir + "fslmaths " + self.path_fmri + "/phase_combined.nii.gz -max -3.1415 -min 3.1415 " +
                self.path_fmri + "/dc/cnlowphase"
            )

            os.system(
                fslDir + "prelude -p " + self.path_fmri + "/dc/cnlowphase.nii.gz -a " +
                self.path_fmri + "/magnitude_combined.nii.gz -o " + self.path_fmri + "/dc/culowphase -m " +
                self.path_fmri + "/magnitude_mask .nii.gz -s"
            )

            culowphase_R = subprocess.check_output(fslDir + "fslstats " + self.path_fmri + "/dc/culowphase.nii.gz -R")
            split_blank1 = culowphase_R[0].split(' ')
            absolute_min = abs(float(split_blank1[0]))

            os.system(
                fslDir + "fslmaths " + self.path_fmri + "/dc/culowphase.nii.gz -add " + str(absolute_min) + " -mas " +
                self.path_fmri + "/dc/mask_magnitude.nii.gz " + self.path_fmri + "/dc/phasemap0"
            )
            os.system(
                fslDir + "fslmaths " + self.path_fmri + "/dc/phasemap0.nii.gz -mul 1000 -div 22 " +
                self.path_fmri + "/dc/fieldmap_rads -odt float"
            )

            os.system(
                fslDir + "fslreorient2std " + self.path_fmri + "/dc/mag_brain.nii.gz " + self.path_fmri + "/dc/std_brain"
            )
            os.system(
                fslDir + "fslreorient2std " + self.path_fmri + "/dc/fieldmap_rads.nii.gz " +
                self.path_fmri + "/dc/std_fieldmap_rads.nii.gz"
            )

            os.system(
                fslDir + "fslroi " + self.path_fmri + "/dc/mean_filtered_func_data_bet.nii.gz " +
                self.path_fmri + "/dc/betfunc0.nii.gz 0 1"
            )
            os.system(
                fslDir + "flirt -in " + self.path_fmri + "/dc/std_brain.nii.gz -ref " +
                self.path_fmri + "/dc/betfunc0.nii.gz -dof 12 -omat " + self.path_fmri + "/dc/mag2func.mat -out " +
                self.path_fmri + "/dc/mag2func1vol.nii.gz"
            )
            os.system(
                fslDir + "flirt -in " + self.path_fmri + "/dc/std_fieldmap_rads.nii.gz -applyxfm -init " +
                "/dc/mag2func.mat -ref " + self.path_fmri + "/dc/betfunc0.nii.gz -out " +
                self.path_fmri + "/dc/fieldmap_rads_reg"
            )
        except:
            print("{}: Error correcting epi distortion".format(self.subjectID))



