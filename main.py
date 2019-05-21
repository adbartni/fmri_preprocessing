#!/usr/bin/ipython

import sys
import re
from collect_raw_data.collect_raw_data import init_fmri_subject_dir, download_raw_fmri_data
from preprocessing.Preprocessing import Preprocessing


class PreprocessingPipeline:

    def __init__(self, input_subject_list):
        self.input_subject_list = input_subject_list

    def pipeline(self):

        subject_list = open(self.input_subject_list)
        for subjectID in subject_list:
            if re.search('[0-9]', subjectID):
                subjectID = check_prefix(subjectID)
                subjectID = subjectID.strip()
            else:
                continue

            print(subjectID)
            init_fmri_subject_dir(subjectID,
                    "/shared/studies/nonregulated/connectome/fmri/subjects/",
                    "/shared/studies/nonregulated/connectome/Subjects/" + subjectID + "/T1w/")

            processing = Preprocessing(subjectID)
            processing.remove_first_two_volumes()
            processing.slicetime_correction()
            processing.motion_correction()
            processing.intensity_normalization()
            processing.temporal_filtering()

            break


def check_prefix(subject):

    if "EX" not in subject:
        subject = "EX" + subject

    return subject

def create_threads(full_subject_list, num_threads):

    for i in range(0, len(full_subject_list), num_threads):
        yield(full_subject_list[i:i + num_threads])


if __name__ == "__main__":

    full_subject_list = sys.argv[1]

    preproc = PreprocessingPipeline(full_subject_list)
    preproc.pipeline()
