import os
import subprocess
from shutil import copyfile, copytree
from .__init__ import fslDir
from .PreMelodicProcessing import Preprocessing


class Melodic(Preprocessing):

    def __init__(self, Preprocessing):

        self.subjectID = Preprocessing.subjectID
        self.path_fmri = Preprocessing.path_fmri
        self.path_HCP = Preprocessing.path_HCP

    def init_melodic_directory(self):
        """
            Sets up files needed for MELODIC to run in /.../<subject>/denoise.ica/
        """

        if not os.path.isdir(self.path_fmri + "/denoise.ica/"):
            os.mkdir(self.path_fmri + "/denoise.ica/")
            os.mkdir(self.path_fmri + "/denoise.ica/filtered_func_data.ica/")

        files = ["mean_func.nii.gz",
                "filtered_func_data_smo.nii.gz"]

        dirs = ["/mc/", "/ants/"]

        for cp_file in files:
            if not os.path.exists(self.path_fmri + "denoise.ica/" + cp_file):
                copyfile(self.path_fmri + cp_file,
                        self.path_fmri + "denoise.ica/" + cp_file)
        if not os.path.exists(self.path_fmri + "denoise.ica/design.fsf"):
            copyfile("/shared/studies/nonregulated/connectome/fmri/subjects/design.fsf",
                    self.path_fmri + "denoise.ica/design.fsf")

        for cp_dir in dirs:
            if not os.path.isdir(self.path_fmri + "/denoise.ica/" + cp_dir):
                copytree(
                    self.path_fmri + cp_dir,
                    self.path_fmri + "/denoise.ica/" + cp_dir
                )

    def ICA(self):

        os.system(
            fslDir + "melodic -i " + self.path_fmri + "/denoise.ica/filtered_func_data_smo.nii.gz -v " + 
            "--outdir=" + self.path_fmri + "/denoise.ica/filtered_func_data.ica/ " + 
            "--mask=" + self.path_fmri + "/mean_epi_in_struct_mask.nii.gz --nobet --bgthreshold=0 --tr=2.5 " +
            "--report --guireport=" + self.path_fmri + "/denoise.ica/filtered_func_data.ica/report.html " +
            "--bgimage=" + self.path_fmri + "/denoise.ica/ants/epi2brain1Warp.nii.gz --mmthresh=0.5 --Ostats --Oorig"
        )
