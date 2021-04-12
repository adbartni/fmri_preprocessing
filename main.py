#!/usr/bin/env python3

import begin
from threading import Thread
from Pipeline import PreprocessingPipeline


def create_threads(full_subject_list, num_threads):
    """ Split the input subject list into a specified number of sublists
        to parellelize the preprocessing pipeline
    """

    for i in range(0, len(full_subject_list), num_threads):
        yield(full_subject_list[i:i + num_threads])


@begin.start
def run(raw_fmri: "Input fMRI nifti",
        t1: "Input T1 aparc aseg nifti",
        stage: "Stage of preprocessing to run",
        qsm: "Susceptibility maps present"
             = False):

    print(raw_fmri)
    print(t1)
    print(stage)
    print(qsm)

    # # Read in subject list from command line argument
    # with open(subject_list_file) as infile:
    #     full_subject_list = infile.read().splitlines()

    # # Split up list into specified number of sublists and run in parellel
    # num_threads = int(num_threads)

    # for thread in create_threads(full_subject_list, num_threads):
    #    preproc = PreprocessingPipeline(thread, stage)
    #    thread_process = Thread(target = preproc.pipeline)
    #    thread_process.start()

