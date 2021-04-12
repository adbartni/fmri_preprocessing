import os
import re
import subprocess
from shutil import copyfile


def init_fmri_subject_dir(fmri, t1, qsm=None):

    copyfile(fmri, "/work/rawfunc.nii.gz")
    copyfile(t1, "/work/T1w_acpc_dc_restore_brain.nii.gz")

    if qsm is not None:
        copyfile(qsm, /work/qsm.nii.gz)

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
