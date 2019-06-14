#!/usr/bin/ipython

import os
import sys
import re
from threading import Thread
from collect_raw_data.collect_raw_data import init_fmri_subject_dir, download_raw_fmri_data
from preprocessing.PreMelodicProcessing import Preprocessing
from preprocessing.StructuralProcessing import StructuralProcessing
from preprocessing.Melodic import Melodic
from preprocessing.PostMelodicProcessing import PostMelodic


class PreprocessingPipeline:

    def __init__(self, subject_list, phase):
        self.subject_list = subject_list
        self.phase = phase.lower()

    def pipeline(self):

        for subjectID in self.subject_list:
            if re.search('[0-9]', subjectID):
                subjectID = check_prefix(subjectID)
                subjectID = subjectID.strip()
            else:
                continue

            if starting_files_present(subjectID) == False:
                print("Skipping {}, not all files present".format(subjectID))
                continue
            else:
                print(subjectID)

            try:
                if self.phase == "melodic":
                    processing = Preprocessing(subjectID)
                    melodic = Melodic(processing)

                    melodic.init_melodic_directory()
                    melodic.ICA()

                elif self.phase == "postmelodic":
                    processing = Preprocessing(subjectID)
                    postmel = PostMelodic(processing)
                    structproc = StructuralProcessing(processing)

                    postmel.denoise()
                    structproc.gm_mask()
                    structproc.csf_mask()
                    structproc.wm_mask()
                    structproc.binarize_masks()
                    postmel.mask_mean_time_series()
                    postmel.create_all_confounds()

                elif self.phase == "premelodic":
                    init_fmri_subject_dir(subjectID,
                                          "/shared/studies/nonregulated/connectome/fmri/subjects/",
                                          "/shared/studies/nonregulated/connectome/Subjects/" + subjectID + "/T1w/")

                    processing = Preprocessing(subjectID)
                    structproc = StructuralProcessing(processing)

                    processing.remove_first_two_volumes()
                    processing.slicetime_correction()
                    processing.motion_correction()
                    processing.intensity_normalization()
                    processing.temporal_mean()
                    processing.temporal_filtering()
                    processing.brain_extraction()
                    processing.epi_distortion_correction()
                    processing.zero_center_fieldmap()

                    structproc.generate_aparcaseg()
                    structproc.downsize_T1()

                    processing.ANTs_registration()
                    processing.motion_outlier_detection()
                    processing.spatial_smoothing()

                elif self.phase == "all":
                    # init_fmri_subject_dir(subjectID,
                    #                       "/shared/studies/nonregulated/connectome/fmri/subjects/",
                    #                       "/shared/studies/nonregulated/connectome/Subjects/" + subjectID + "/T1w/")

                    processing = Preprocessing(subjectID)
                    structproc = StructuralProcessing(processing)
                    # melodic = Melodic(processing)
                    postmel = PostMelodic(processing)

                    # processing.remove_first_two_volumes()
                    # processing.slicetime_correction()
                    # processing.motion_correction()
                    # processing.intensity_normalization()
                    # processing.temporal_mean()
                    # processing.temporal_filtering()
                    # processing.brain_extraction()
                    # processing.epi_distortion_correction()
                    # processing.zero_center_fieldmap()

                    # structproc.generate_aparcaseg()
                    # structproc.downsize_T1()
                    #
                    # processing.ANTs_registration()
                    # processing.motion_outlier_detection()
                    # processing.spatial_smoothing()
                    #
                    # melodic.init_melodic_directory()
                    # melodic.ICA()
                    # postmel.denoise()

                    structproc.gm_mask()
                    structproc.csf_mask()
                    structproc.wm_mask()
                    structproc.binarize_masks()

                    postmel.mask_mean_time_series()
                    postmel.create_all_confounds()

            except:
                print("{}: Something went wrong".format(subjectID))
                pass

            break


def starting_files_present(subjectID):

    path_conntectome = "/shared/studies/nonregulated/connectome/"
    functional_data = path_conntectome + "fmri/subjects/" + subjectID + "/rawfunc.nii.gz"
    structural_data = path_conntectome + "Subjects/" + subjectID + "/T1w/T1w_acpc_dc_restore_brain.nii.gz"
    QSM_path = "/shared/studies/nonregulated/qsm_repo/data/" + subjectID.replace("EX","") + "/recon/"

    if (not os.path.exists(functional_data)
            or not os.path.exists(structural_data)
            or not os.path.exists(QSM_path + "magnitude_combined.nii.gz")
            or not os.path.exists(QSM_path + "phase_combined.nii.gz")):
        return False
    else:
        return True


def check_prefix(subject):

    if "EX" not in subject:
        subject = "EX" + subject

    return subject


def create_threads(full_subject_list, num_threads):

    for i in range(0, len(full_subject_list), num_threads):
        yield(full_subject_list[i:i + num_threads])


if __name__ == "__main__":

    with open(sys.argv[1]) as infile:
        full_subject_list = infile.read().splitlines()

    # phase = sys.argv[2]
    # print(phase)
    # preproc = PreprocessingPipeline(full_subject_list, phase)
    # preproc.pipeline()
    num_threads = int(sys.argv[2])
    phase = sys.argv[3]

    for thread in create_threads(full_subject_list, num_threads):
       preproc = PreprocessingPipeline(thread, phase)
       thread_process = Thread(target = preproc.pipeline)
       thread_process.start()