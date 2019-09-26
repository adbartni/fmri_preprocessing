#!/usr/bin/env python

import begin
import os
import sys
import re
from threading import Thread
from collect_raw_data.collect_raw_data import init_fmri_subject_dir, download_raw_fmri_data
from preprocessing.PreMelodicProcessing import Preprocessing
from preprocessing.StructuralProcessing import StructuralProcessing
from preprocessing.Melodic import Melodic
from preprocessing.PostMelodicProcessing import PostMelodic
from connectome_analyses.FunctionalConnectivity import FunctionalConnectome


class PreprocessingPipeline:
    """ Wraps a subject in the entire preprocessing pipeline
        
        Allows for parellelization and easy management of which
        stages of preprocessing are used
    """

    def __init__(self, subject_list, phase):
        self.subject_list = subject_list
        self.phase = phase.lower()

    def pipeline(self):
        """ Monolithic method that contains the entire preprocessing pipeline

            Stages of preprocessing are specified via command line args:
                Premelodic - initial preprocessing steps on time series,
                             including volume removal, slicetime correction,
                             motion correction, distortion correction,
                             registration into T1 space, etc.
                Melodic - independent component analysis across time series;
                             as of now, hand denoising MUST be done after this step
                Postmelodic - Removal of noise components, spatial smoothing,
                             masking of confounds, and generation of 
                             functional connectome for each subject
                All - << DON'T ACTUALLY DO THIS UNTIL FIX IS WORKING >>
                             Run the entire pipeline at once; 
        """

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
                if self.phase == "premelodic":
                    init_fmri_subject_dir(subjectID,
                                          "/shared/studies/nonregulated/connectome/fmri/subjects/",
                                          "/shared/studies/nonregulated/connectome/Subjects/" + subjectID + "/T1w/")

                    processing = Preprocessing(subjectID)
                    structproc = StructuralProcessing(processing)
                    melodic = Melodic(processing)

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

                    melodic.init_melodic_directory()
                    melodic.ICA()
                    
                elif self.phase == "melodic":
                    melodic = Melodic(processing)

                    melodic.init_melodic_directory()
                    melodic.ICA()

                elif self.phase == "postmelodic":
                    processing = Preprocessing(subjectID)
                    postmel = PostMelodic(processing)
                    structproc = StructuralProcessing(processing)
                    fcon = FunctionalConnectome(subjectID)

                    postmel.denoise()
                    structproc.gm_mask()
                    structproc.csf_mask()
                    structproc.wm_mask()
                    structproc.binarize_masks()
                    postmel.mask_mean_time_series()
                    postmel.create_all_confounds()
                    
                    fcon.create_functional_connectivity_matrix()

                elif self.phase == "all":
                    """ 
                    <<< DON'T USE THIS UNTIL FIX IS WORKING >>> 
                    """
                    init_fmri_subject_dir(subjectID,
                                           "/shared/studies/nonregulated/connectome/fmri/subjects/",
                                           "/shared/studies/nonregulated/connectome/Subjects/" + subjectID + "/T1w/")

                    processing = Preprocessing(subjectID)
                    structproc = StructuralProcessing(processing)
                    melodic = Melodic(processing)
                    postmel = PostMelodic(processing)
                    fcon = FunctionalConnectome(subjectID)

                    processing.remove_first_two_volumes()
                    processing.slicetime_correction()
                    processing.motion_correction()
                    processing.intensity_normalization()
                    processing.temporal_mean()
                    processing.brain_extraction()
                    processing.epi_distortion_correction()
                    processing.zero_center_fieldmap()

                    structproc.generate_aparcaseg()
                    structproc.downsize_T1()
                    
                    processing.ANTs_registration()
                    processing.motion_outlier_detection()
                    processing.spatial_smoothing()
                    
                    melodic.init_melodic_directory()
                    melodic.ICA()
                    # FIX would go here
                    # FIX **is** currently working, need to add to pipeline
                    postmel.denoise()
                    postmel.temporal_filtering()

                    structproc.gm_mask()
                    structproc.csf_mask()
                    structproc.wm_mask()
                    structproc.binarize_masks()

                    postmel.mask_mean_time_series()
                    postmel.create_all_confounds()

                    fcon.create_functional_connectivity_matrix()

                else:
                    # Function to match single step specified 
                    # at cli will go here once it's working
                    pass

            except:
                print("{}: Something went wrong".format(subjectID))
                pass



def starting_files_present(subjectID):
    """ Verify that each subject has:
            Fully processed strucutral image (T1 freesurfer output)
            Unprocessed raw functional image from bluesky
            QSM fieldmap images (magnitude and phase images)
        before beginning processing
    """

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
    """ Append 'EX' to subject's ID if necessary
    """

    if "EX" not in subject:
        subject = "EX" + subject

    return subject


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

