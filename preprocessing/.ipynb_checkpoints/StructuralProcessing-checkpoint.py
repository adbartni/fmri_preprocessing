import os
import subprocess
import re
from __init__ import fslDir
from PreMelodicProcessing import Preprocessing


class StructuralProcessing(Preprocessing):

    mc_path = "/shared/software/vendor/freesurfer/freesurfer-5.3.0_x86_64/bin/"
    tk_path = "/shared/software/vendor/freesurfer/freesurfer-5.3.0_x86_64/tktools/"

    def __init__(self, Preprocessing):
        self.subjectID = Preprocessing.subjectID
        self.path_HCP = Preprocessing.path_HCP

    def generate_aparcaseg(self):
        os.system(
            self.mc_path + "mri_convert " + self.path_HCP + self.subjectID + "/mri/aparc+aseg.mgz " +
            self.path_HCP + "/aparc_aseg_fs.nii.gz"
        )
        os.system(
            self.tk_path + "tkregister2 --mov " + self.path_HCP + self.subjectID + "/mri/orig.mgz " +
            "--targ " + self.path_HCP + self.subjectID + "/mri/rawavg.mgz " +
            "--regheader --reg junk --fslregout " + self.path_HCP + self.subjectID +
            "/freesurfer2struct.mat --noedit"
        )
        os.system(
            fslDir + "flirt -in " + self.path_HCP + "/aparc_aseg_fs.nii.gz " +
            "-ref " + self.path_HCP + "/T1w_acpc_dc_restore.nii.gz " +
            "-applyxfm -init " +
            self.path_HCP + self.subjectID + "/freesurfer2struct.mat -interp nearestneighbour " +
            "-out " + self.path_HCP + "/aparc+aseg.nii.gz"
        )


    def downsize_T1(self):

        os.system(
            fslDir + "flirt -interp spline -in " + self.path_HCP + "/T1w_acpc_dc_restore.nii.gz -ref " +
            self.path_HCP + "/T1w_acpc_dc_restore.nii.gz -applyisoxfm 2.0 -out " +
            self.path_HCP + "/T1w_acpc_dc_restore_2.00.nii.gz"
        )
        os.system(
            fslDir + "flirt -interp spline -in " + self.path_HCP + "/T1w_acpc_dc_restore_brain.nii.gz -ref " +
            self.path_HCP + "/T1w_acpc_dc_restore_brain.nii.gz -applyisoxfm 2.0 -out " +
            self.path_HCP + "/T1w_acpc_dc_restore_brain_2.00.nii.gz"
        )


    def gm_mask(self):

        segments = [8]
        for i in range(10,14):
            segments.append(i)
        segments.append(17)
        segments.append(18)
        segments.append(26)
        segments.append(28)
        segments.append(47)
        for i in range(49,55):
            segments.append(i)
        segments.append(58)
        segments.append(60)

        for i in range(1001,1036):
            if i != 1004:
                segments.append(i)

        for i in range(2001,2036):
            if i != 2004:
                segments.append(i)

        threshold_additon_cmd = fslDir + "fslmaths " + self.path_HCP
        for seg in segments:
            if segments.index(seg) == 0:
                threshold_additon_cmd += "/GMmask" + str(seg) + ".nii.gz "
            else:
                threshold_additon_cmd += "-add " + self.path_HCP + "/GMmask" + str(seg) + ".nii.gz "

            os.system(
                fslDir + "fslmaths " + self.path_HCP + "/aparc+aseg.nii.gz -thr " + str(seg - 0.5) +
                " -uthr " + str(seg + 0.5) + " " + self.path_HCP + "/GMmask" + str(seg) + ".nii.gz"
            )

        threshold_additon_cmd += " " + self.path_HCP + "/GMmask.nii.gz"
        os.system(threshold_additon_cmd)
        
        for index in segments:
            temp_img = "GMmask" + str(index) + ".nii.gz"
            os.remove(os.path.join(self.path_HCP, temp_img))


    def csf_mask(self):

        segments = [4,5,14,15,24,43,44]
        threshold_additon_cmd = fslDir + "fslmaths " + self.path_HCP
        for seg in segments:
            if segments.index(seg) == 0:
                threshold_additon_cmd += "/CSFmask" + str(seg) + ".nii.gz "
            else:
                threshold_additon_cmd += "-add " + self.path_HCP + "/CSFmask" + str(seg) + ".nii.gz "

            os.system(
                fslDir + "fslmaths " + self.path_HCP + "/aparc+aseg.nii.gz -thr " + str(seg - 0.5) +
                " -uthr " + str(seg + 0.5) + " " + self.path_HCP + "/CSFmask" + str(seg) + ".nii.gz"
            )

        threshold_additon_cmd += " " + self.path_HCP + "/CSFmask.nii.gz"
        os.system(threshold_additon_cmd)
        
        for index in segments:
            temp_img = "CSFmask" + str(index) + ".nii.gz"
            os.remove(os.path.join(self.path_HCP, temp_img))


    def wm_mask(self):

        segments = [2,7,41,46]
        threshold_additon_cmd = fslDir + "fslmaths " + self.path_HCP
        for seg in segments:
            if segments.index(seg) == 0:
                threshold_additon_cmd += "/WMmask" + str(seg) + ".nii.gz "
            else:
                threshold_additon_cmd += "-add " + self.path_HCP + "/WMmask" + str(seg) + ".nii.gz "

            os.system(
                fslDir + "fslmaths " + self.path_HCP + "/aparc+aseg.nii.gz -thr " + str(seg - 0.5) +
                " -uthr " + str(seg + 0.5) + " " + self.path_HCP + "/WMmask" + str(seg) + ".nii.gz"
            )

        threshold_additon_cmd += " " + self.path_HCP + "/WMmask.nii.gz"
        os.system(threshold_additon_cmd)
        
        for index in segments:
            temp_img = "WMmask" + str(index) + ".nii.gz"
            os.remove(os.path.join(self.path_HCP, temp_img))


    def binarize_masks(self):

        mask_types = ["WM", "GM", "CSF"]
        for mask in mask_types:
            if mask == "GM":
                os.system(
                        fslDir + "flirt -interp nearestneighbour -in " + self.path_HCP + mask + "mask.nii.gz " + 
                        "-ref " + self.path_HCP + mask + "mask.nii.gz -applyisoxfm 2.0 " + 
                        "-out " + self.path_HCP + mask + "mask_2.00.nii.gz"
                )
                os.system(
                        fslDir + "fslmaths " + self.path_HCP + mask + "mask_2.00.nii.gz -bin " + 
                        self.path_HCP + mask + "mask_bin_2.00.nii.gz"
                )

            else:
                os.system(
                    fslDir + "fslmaths " + self.path_HCP + "/" + mask + "mask.nii.gz -bin " +
                    self.path_HCP + "/" + mask + "mask_bin.nii.gz"
                )
                os.system(
                    fslDir + "flirt -interp nearestneighbour -in " + self.path_HCP + "/" + mask + "mask_bin.nii.gz " +
                    "-ref " + self.path_HCP + "/" + mask + "mask_bin.nii.gz" +
                    " -applyisoxfm 2.0 " +
                    " -out " + self.path_HCP + "/" + mask + "mask_bin_2.00.nii.gz"
                )

