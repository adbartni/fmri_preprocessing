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

    def __init__(self, subject_list):
        self.subject_list = subject_list

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

            print(subjectID)
            init_fmri_subject_dir(subjectID,
                    "/shared/studies/nonregulated/connectome/fmri/subjects/",
                    "/shared/studies/nonregulated/connectome/Subjects/" + subjectID + "/T1w/")

            processing = Preprocessing(subjectID)
            structproc = StructuralProcessing(processing)
            melodic = Melodic(processing)
            postmel = PostMelodic(processing)

            try:
                # print("Removing first two volumes")
                #processing.remove_first_two_volumes()
                # print("Slicetime correction")
                #processing.slicetime_correction()
                # print("Motion correction")
                #processing.motion_correction()
                # print("Intensity normalization")
                #processing.intensity_normalization()
                # print("Temporal mean")
                #processing.temporal_mean()
                # print("Temporal filtering")
                #processing.temporal_filtering()
                # print("Brain extraction")
                #processing.brain_extraction()
                # print("Epi distortion correction")
                #processing.epi_distortion_correction()
                # print("Zero centering fieldmap")
                #processing.zero_center_fieldmap()

                # print("Generating aparc+aseg")
                structproc.generate_aparcaseg()
                # print("Downsizing T1")
                structproc.downsize_T1()

                # print("Fugue")
                #processing.fugue()
                # print("ANTs")
                processing.ANTs_registration()
                # print("Motion outlier detection")
                processing.motion_outlier_detection()
                # print("Spatial smoothing")
                processing.spatial_smoothing()

                melodic.init_melodic_directory()
                melodic.ICA()

                # postmel.denoise()

            except:
                print("{}: Something went wrong".format(subjectID))
                pass

            # break


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

    # preproc = PreprocessingPipeline(full_subject_list)
    # preproc.pipeline()
    num_threads = int(sys.argv[2])

    for thread in create_threads(full_subject_list, num_threads):
       preproc = PreprocessingPipeline(thread)
       thread_process = Thread(target = preproc.pipeline)
       thread_process.start()
