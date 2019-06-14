#!/bin/bash

cat /shared/studies/nonregulated/connectome/fmri/preprocessing_pipeline/missing_subs.txt | while read line; do
    sub=$line
    cd /shared/studies/nonregulated/connectome/Subjects/$sub/T1w/
    #   find . -type d -exec chmod g+rwx {} \;
       sudo find . -type f -exec chmod g+rw {} \;
       echo $sub
done
