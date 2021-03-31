#!/usr/bin/env python

import begin
from threading import Thread
from Pipeline import PreprocessingPipeline


def create_threads(full_subject_list, num_threads):
    """ Split the input subject list into a specified number of sublists
        to parellelize the preprocessing pipeline
    """

    for i in range(0, len(full_subject_list), num_threads):
        yield(full_subject_list[i:i + num_threads])


## FOR BEGINNERS ##
# Anything defined after the begin.start decorator will be run automatically;
# Arguments for anything defined here are used as command line arguments;
@begin.start
def run(subject_list_file: "Subject list",
        num_threads: "Number of threads",
        stage: "Stage of preprocessing to run",
        step: "To run only one step of the pipeline" = None,
        cleanup: "Clean up intermediary files generated during processing"
             = False):

    # Read in subject list from command line argument
    with open(subject_list_file) as infile:
        full_subject_list = infile.read().splitlines()

    # Split up list into specified number of sublists and run in parellel
    num_threads = int(num_threads)

    for thread in create_threads(full_subject_list, num_threads):
       preproc = PreprocessingPipeline(thread, stage)
       thread_process = Thread(target = preproc.pipeline)
       thread_process.start()

