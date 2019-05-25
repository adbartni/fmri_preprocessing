import os
import subprocess
from shutil import copyfile


def init_fmri_subject_dir(subjectID, path_fmri, path_HCP):

    ## Create subject directory if it does not exist
    if not os.path.isdir(path_fmri  + subjectID):
        os.mkdir(path_fmri + subjectID)

    ## Copy brainmask into fmri subject directory
    copyfile(path_HCP + "/T1w_acpc_dc_restore_brain.nii.gz", path_fmri + subjectID + "/brainmask.nii.gz")

    ## Copy QSM data to fmri subject directory
    strippedID = subjectID[2:]
    path_QSM = os.path.join("/shared/studies/nonregulated/qsm_repo/data/", strippedID + "/recon/")
    if os.path.isdir(path_QSM):
        for qsm_file in ["magnitude_combined.nii.gz", "phase_combined.nii.gz"]:
            copyfile(os.path.join(path_QSM, qsm_file), os.path.join(path_fmri, subjectID + "/" + qsm_file))

        else:
            print("{}: Not in QSM repo".format(subjectID))


def download_raw_fmri_data(subjectID, path_fmri):

    BBS_info = "bluesky_info -i BBS -o " + subjectID + " | grep 'FMRI RESTING STATE' | cut -d"|" -f2 | sort -n | head -n 1"
    try:
        fmriID = subprocess.check_output(BBS_info, shell=True)
        fmriID = ''.join(fmriID)

        os.system("bluesky_retriever -i BBS -o " + os.path.join(path_fmri, subjectID, fmriID))
        # os.rename(os.path.join(path_fmri, subjectID, fmriID), os.path.join(path_fmri, subjectID, "rawfunc.nii.gz"))

    except:
        print("{}: Something wrong".format(subjectID))
