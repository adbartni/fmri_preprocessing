#!/usr/bin/ipython

import os
import sys
import re
from threading import Thread
from collect_raw_data.collect_raw_data import init_fmri_subject_dir, download_raw_fmri_data
from preprocessing.PreMelodicProcessing import Preprocessing
from preprocessing.StructuralProcessing import StructuralProcessing


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

            if verify_necessary_files == False:
                continue

            print(subjectID)
            init_fmri_subject_dir(subjectID,
                    "/shared/studies/nonregulated/connectome/fmri/subjects/",
                    "/shared/studies/nonregulated/connectome/Subjects/" + subjectID + "/T1w/")

            processing = Preprocessing(subjectID)
            structproc = StructuralProcessing(processing)

            try:
                processing.remove_first_two_volumes()
                processing.slicetime_correction()
                processing.motion_correction()
                processing.intensity_normalization()
                processing.temporal_mean()
                processing.temporal_filtering()
                processing.brain_extraction()
                processing.epi_distortion_correction()
                processing.zero_center_fieldmap()
                processing.fugue()
                processing.ANTs_registration()
                processing.motion_outlier_detection()
                processing.spatial_smoothing()

                structproc.generate_aparcaseg()
                structproc.downsize_T1()

            except:
                print("{}: Something went wrong".format(subjectID))
                pass

            #break


def verify_necessary_files(subjectID):

    functional_data = "/shared/studies/nonregulated/connectome/fmri/subjects/" + subjectID + "/rawfunc.nii.gz"
    structural_data = "/shared/studies/nonregulated/connectome/Subjects/" + subjectID + "/T1w/T1w_acpc_dc_restore_brain.nii.gz"
    QSM_data = "/shared/studies/nonregulated/qsm_repo/data/" + subjectID.replace("EX","")

    if not os.path.exists(functional_data) or not os.path.exists(structural_data) or not os.path.isdir(QSM_data):
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

    num_threads = int(sys.argv[2])

    for thread in create_threads(full_subject_list, num_threads):
        preproc = PreprocessingPipeline(thread)
        thread_process = Thread(target = preproc.pipeline)
        thread_process.start()
    
