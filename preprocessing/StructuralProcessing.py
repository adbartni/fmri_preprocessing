import os
import subprocess
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

