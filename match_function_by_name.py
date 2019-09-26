#!/usr/bin/env python

import inspect
from collect_raw_data.collect_raw_data import init_fmri_subject_dir, download_raw_fmri_data
from preprocessing.PreMelodicProcessing import Preprocessing
from preprocessing.StructuralProcessing import StructuralProcessing
from preprocessing.Melodic import Melodic
from preprocessing.PostMelodicProcessing import PostMelodic
from connectome_analyses.FunctionalConnectivity import FunctionalConnectome


def match(subjectID, function):

    processing = Preprocessing(subjectID)
    structproc = StructuralProcessing(processing)
    melodic = Melodic(processing)
    postmel = PostMelodic(processing)

    premel_funcs = inspect.getmembers(processing, predicate=inspect.ismethod)
    mel_funcs = inspect.getmembers(melodic, predicate=inspect.ismethod)
    postmel_funcs = inspect.getmembers(postmel, predicate=inspect.ismethod)
    struct_funcs = inspect.getmembers(structproc, predicate=inspect.ismethod)

    functions = {}
    for func in premel_funcs:
        functions[func[0]] = func[1]
    for func in mel_funcs:
        functions[func[0]] = func[1]
    for func in postmel_funcs:
        functions[func[0]] = func[1]
    for func in struct_funcs:
        functions[func[0]] = func[1]

    for function_name, function_object in functions.items():
        if function == function_name:
            if function in [subname[0] for subname in premel_funcs]:
                print(function_object)
                return(processing.function_object)
            else:
                return(function_object)

if __name__ == "__main__":
        function = match("EX54589", "epi_distortion_correction")
        print(function)
