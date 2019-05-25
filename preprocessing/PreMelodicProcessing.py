import os
import subprocess
from shutil import copyfile
from __init__ import fslDir


class Preprocessing:

    def __init__(self, subjectID):
        self.subjectID = subjectID
        self.path_fmri = "/shared/studies/nonregulated/connectome/fmri/subjects/" + subjectID + "/"
        self.path_HCP = "/shared/studies/nonregulated/connectome/Subjects/" + subjectID + "/T1w/"
        self.mc_path = "/shared/software/vendor/freesurfer/freesurfer-5.3.0_x86_64/bin/"
        self.ants_path = "/usr/lib/ants/"

    def remove_first_two_volumes(self):
        os.system(
            fslDir + "fslroi " + self.path_fmri + "/rawfunc.nii.gz " +
            self.path_fmri + "/prefiltered_func_data_2cut 2 238"
        )


    def slicetime_correction(self):
        os.system(
            fslDir + "slicetimer -i " + self.path_fmri + "/prefiltered_func_data_2cut -o " +
            self.path_fmri + "/prefiltered_func_data_st -r 2.5 --odd"
        )


    def motion_correction(self):
        if not os.path.isdir(os.path.join(self.path_fmri, "mc")):
            os.mkdir(os.path.join(self.path_fmri, "mc"))
        os.system(
            fslDir + "mcflirt -in " + self.path_fmri + "/prefiltered_func_data_st.nii.gz" +
            " -out " + self.path_fmri + "/mc/prefiltered_func_data_mcf -plots -spline_final -mats -rmsrel -rmsabs"
        )
        copyfile(os.path.join(self.path_fmri, "mc/prefiltered_func_data_mcf.nii.gz"),
                 os.path.join(self.path_fmri, "prefiltered_func_data_mcf.nii.gz"))


    def intensity_normalization(self):
        os.system(
            fslDir + "fslmaths " + self.path_fmri + "prefiltered_func_data_mcf.nii.gz -ing 10000 " +
            self.path_fmri + "/prefiltered_func_data_in -odt float"
        )


    def temporal_mean(self):
        os.system(
            fslDir + "fslmaths " + self.path_fmri + "/prefiltered_func_data_in.nii.gz -Tmean " +
            self.path_fmri + "/tempMean"
        )


    def temporal_filtering(self):
        os.system(
            fslDir + "fslmaths " + self.path_fmri + "/prefiltered_func_data_in.nii.gz -bptf 400 -1 -add " +
            self.path_fmri + "/tempMean.nii.gz " + self.path_fmri + "/filtered_func_data"
        )


    def brain_extraction(self):
        os.system(
            fslDir + "fslmaths " + self.path_fmri + "/filtered_func_data.nii.gz -Tmean " +
            self.path_fmri + "/mean_func_filtered"
        )
        os.system(
            fslDir + "bet2 " + self.path_fmri + "/mean_func_filtered " +
            self.path_fmri + "/filtered_mask -f 0.3 -n -m"
        )
        os.system(
            fslDir + "immv " + self.path_fmri + "/filtered_mask_mask " + self.path_fmri + "/filtered_mask"
        )
        os.system(
            fslDir + "fslmaths " + self.path_fmri + "/filtered_func_data.nii.gz -mas " +
            self.path_fmri + "/filtered_mask " + self.path_fmri + "/filtered_func_data_bet.nii.gz"
        )

        if not os.path.isdir(os.path.join(self.path_fmri, "dc")):
            os.mkdir(os.path.join(self.path_fmri, "dc"))
        os.system(
            fslDir + "fslmaths " + self.path_fmri + "/magnitude_combined.nii.gz -Tmean " +
            self.path_fmri + "/mean_magnitude_combined"
        )
        os.system(
            fslDir + "bet2 " + self.path_fmri + "/mean_magnitude_combined " +
            self.path_fmri + "/magnitude_mask -f 0.3 -n -m"
        )
        os.system(
            fslDir + "immv " + self.path_fmri + "/magnitude_mask_mask " + self.path_fmri + "/magnitude_mask"
        )
        os.system(
            fslDir + "fslmaths " + self.path_fmri + "/magnitude_combined.nii.gz -mas " +
            self.path_fmri + "/magnitude_mask " + self.path_fmri + "/dc/mag_brain.nii.gz"
        )


    # Should really consider breaking this up at some point
    def epi_distortion_correction(self):
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
            self.path_fmri + "/magnitude_mask.nii.gz -s"
        )

        culowphase_R = subprocess.check_output(fslDir + "fslstats " + self.path_fmri + "/dc/culowphase.nii.gz -R",
                shell = True)
        split_blank1 = culowphase_R.split(' ')
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
            self.path_fmri + "/dc/mag2func.mat -ref " + self.path_fmri + "/dc/betfunc0.nii.gz -out " +
            self.path_fmri + "/dc/fieldmap_rads_reg"
        )


    def zero_center_fieldmap(self):
        os.system(
            fslDir + "fslmaths "  + self.path_fmri + "/dc/fieldmap_rads.nii.gz -kernel 3D -ero -kernel 2D -ero -ero " +
            self.path_fmri + "/dc/fieldmap_rads_ero.nii.gz"
            )
        os.system(
            fslDir + "fslmaths " + self.path_fmri + "/dc/fieldmap_rads_ero.nii.gz -dilM -dilM -dilM " +
            self.path_fmri + "/dc/fieldmap_rads_dil.nii.gz"
            )
        os.system(
            fslDir + "fslmaths " + self.path_fmri + "/dc/fieldmap_rads.nii.gz -bin -mul -1 -add 1 -mul " +
            self.path_fmri + "/dc/fieldmap_rads_dil.nii.gz -add "  + self.path_fmri + "/dc/fieldmap_rads.nii.gz " +
            self.path_fmri + "/dc/fieldmap_rads_dil_inside.nii.gz"
        ) 

        os.system(
            fslDir + "fslreorient2std " + self.path_fmri + "/dc/fieldmap_rads_dil_inside.nii.gz " +
            self.path_fmri + "/dc/std_fieldmap_rads.nii.gz"
        )
        os.system(
            self.mc_path + "mri_convert -vs 2 2 2 " + self.path_fmri + "/dc/std_fieldmap_rads.nii.gz " +
            self.path_fmri + "/dc/std_fieldmap_rads_2mm.nii.gz"
        )

        os.system(
            fslDir + "flirt -in " + self.path_fmri + "/dc/std_fieldmap_rads_2mm.nii.gz -ref " +
            self.path_fmri + "/dc/mean_filtered_func_data_bet.nii.gz -out " +
            self.path_fmri + "/dc/fieldmap2epi.nii.gz"
        )

        os.system(
            fslDir + "bet " + self.path_fmri + "/dc/fieldmap2epi.nii.gz " + self.path_fmri + "/dc/fmap.nii.gz -m"
        )

        weighted_avg = subprocess.check_output(
            fslDir + "fslstats " + self.path_fmri + "/dc/fieldmap2epi.nii.gz -k " +
            self.path_fmri + "/dc/fmap_mask.nii.gz -m",
            shell = True
        )
        weighted_avg = weighted_avg.split(' ')
        weighted_avg = abs(float(weighted_avg[0]))

        os.system(
            fslDir + "fslmaths  " + self.path_fmri + "/dc/fmap_mask.nii.gz -kernel 3D  -ero -ero -ero -kernel 2D " +
            "-ero -ero " + self.path_fmri + "/dc/fmap_mask_ero"
        )
        os.system(
            fslDir + "fslmaths " + self.path_fmri + "/dc/fmap_mask_ero.nii.gz -kernel 2D -dilD  -dilM -kernel 3D " +
            "-dilM -dilD " + self.path_fmri + "/dc/fmap_mask_dil.nii.gz"
        )

        os.system(
            fslDir + "fslmaths " + self.path_fmri + "/dc/fieldmap2epi.nii.gz -sub " + str(weighted_avg)  +
            " " + self.path_fmri + "/dc/fieldmap2epi_mean_centered.nii.gz"
        )
        os.system(
            fslDir + "fslmaths " + self.path_fmri + "/dc/fieldmap2epi_mean_centered.nii.gz -mul " +
        self.path_fmri + "/dc/fmap_mask_dil.nii.gz " + self.path_fmri + "/dc/fieldmap2epi_mean_centered_0outside.nii.gz"
        )


    def fugue(self):
        os.system(
            fslDir + "fugue -i " + self.path_fmri + "/filtered_func_data_bet.nii.gz --loadfmap=" +
            self.path_fmri + "/dc/fieldmap2epi_mean_centered_0outside.nii.gz --dwell=0.0002 --unwarpdir=y- -u " +
            self.path_fmri + "/dc/unwarped.nii.gz"
        )


    def ANTs_registration(self):
        if not os.path.isdir(os.path.join(self.path_fmri, "ants")):
            os.mkdir(os.path.join(self.path_fmri, "ants"))

        os.system(
           self.ants_path + "antsRegistrationSyN.sh -d 3 -f " + 
           self.path_HCP + "/T1w_acpc_dc_restore_brain_2.00.nii.gz -m " +
           self.path_fmri + "/dc/unwarped.nii.gz -o " + self.path_fmri + "/ants/epi2brain -n 32 -t s"
        )
        os.system(
            self.ants_path + "antsApplyTransforms -d 3 -i " + self.path_fmri + "/dc/unwarped.nii.gz -e 3 -r " +
            self.path_HCP + "/T1w_acpc_dc_restore_brain_2.00.nii.gz -o " +
            self.path_fmri + "/ants/epi2braints.nii.gz -n NearestNeighbor -t " +
            self.path_fmri + "/ants/epi2brain1Warp.nii.gz -t " + self.path_fmri + "/ants/epi2brain0GenericAffine.mat"
        )


    def motion_outlier_detection(self):
        os.system(
            fslDir + "fsl_motion_outliers -i " + self.path_fmri + "/ants/epi2braints.nii.gz --nomoco -o " +
            self.path_fmri + "/outlier_detection.mat"
        )


    def spatial_smoothing(self):
        os.system(
            fslDir + "bet2 " + self.path_fmri + "/ants/epi2brainWarped.nii.gz " +
            self.path_fmri + "/mean_epi_in_struct -f 0.3 -n -m"
        )

        func2struc_p50 = subprocess.check_output(
            fslDir + "fslstats " + self.path_fmri + "/ants/epi2brainWarped.nii.gz -k " +
            self.path_fmri + "/mean_epi_in_struct_mask.nii.gz -p 50",
            shell = True
        )
        thr3 = 0.75 * float(func2struc_p50[0])

        os.system(
            fslDir + "fslmaths " + self.path_fmri + "/mean_epi_in_struct_mask.nii.gz -dilF " +
            self.path_fmri + "/mean_epi_in_struct_mask.nii.gz"
        )
        os.system(
            fslDir + "fslmaths " + self.path_fmri + "/ants/epi2braints.nii.gz -mas " +
            self.path_fmri + "/mean_epi_in_struct_mask.nii.gz " + self.path_fmri + "/filtered_func_data_thr.nii.gz"
        )
        os.system(
            fslDir + "fslmaths " + self.path_fmri + "/filtered_func_data_thr.nii.gz -Tmean " +
            self.path_fmri + "/mean_func"
        )

        os.system(
            fslDir + "susan " + self.path_fmri + "/filtered_func_data_thr.nii.gz " + str(thr3) +
            " 1.698513800424628 3 1 1 " + self.path_fmri + "/mean_func.nii.gz " + str(thr3) +
            " " + self.path_fmri + "/filtered_func_data_smo.nii.gz"
        )
        os.system(
            fslDir + "fslmaths " + self.path_fmri + "/filtered_func_data_smo.nii.gz -mas " +
            self.path_fmri + "/mean_epi_in_struct_mask.nii.gz " + self.path_fmri + "/filtered_func_data_smo.nii.gz"
        )


