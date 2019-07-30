import os
import re
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
    if os.path.isdir(path_QSM) and not os.path.exists(path_fmri + subjectID + "/phase_combined.nii.gz"):
        for qsm_file in ["magnitude_combined.nii.gz", "phase_combined.nii.gz"]:
            copyfile(os.path.join(path_QSM, qsm_file), os.path.join(path_fmri, subjectID + "/" + qsm_file))

    elif not os.path.exists(path_QSM + "/phase_combined.nii.gz"):
        print("{}: Missing QSM".format(subjectID))


def download_raw_fmri_data(subjectID, path_fmri):

    BBS_info = subprocess.check_output("bluesky_info -i BBS -o " + subjectID, shell=True)
    BBS_info_list = BBS_info.splitlines()
    
    fmriID = ""
    for line in BBS_info_list:
        if "FMRI" in line:
            fmriID = re.search(r'MR[0-9]*', line).group()
        else:
            pass
    
    try:
        os.chdir(os.path.join(path_fmri, subjectID))
        raw_name = subprocess.check_output("bluesky_retriever -i BBS -o " + fmriID, shell=True)
        os.system("bluesky_retriever -i BBS -o " + fmriID)
        if not os.path.exists("rawfunc.nii.gz"):
            os.rename(raw_name, "rawfunc.nii.gz")

    except:
        print("{}: Couldn't download raw functional data".format(subjectID))
