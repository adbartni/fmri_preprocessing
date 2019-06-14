#!/usr/bin/ipython

import os
import sys
from main import starting_files_present


subs = [subject.replace('\n','').strip() for subject in open('missing_subs.txt', 'r').readlines()]
source_dir = sys.argv[1]
filename = sys.argv[2]

for sub in subs:
    path_fmri = "/shared/studies/nonregulated/connectome/fmri/subjects/" + sub
    path_HCP = "/shared/studies/nonregulated/connectome/Subjects/" + sub + "/T1w/"

    if source_dir == "fmri":
        look_in = path_fmri
    elif source_dir == "t1":
        look_in = path_HCP

    if starting_files_present(sub) == False:
        continue

    if os.path.exists(look_in + "/" + filename):
        print("{}: {} found".format(sub, filename))
    else:
        print("{}: {} not found".format(sub, filename))

