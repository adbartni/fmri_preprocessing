#!/usr/bin/env python

import os
import sys


subject_list_file = sys.argv[1]
with open(subject_list_file) as infile:
    subject_list = infile.read().splitlines()

path_fmri = '/shared/nonrestricted/connectome/fmri/subjects/'

if not os.path.isdir('reports'):
    os.mkdir('reports')

for subjectID in subject_list:

    if not os.path.isdir(os.path.join('reports',subjectID)):
        os.mkdir(os.path.join('reports',subjectID))

