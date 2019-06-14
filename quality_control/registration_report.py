from init_reports_directory import subject_list, path_fmri
from nilearn import plotting, image
import nibabel
import os


subjects_as_string = ""
for subjectID in subject_list:

    reg_func_file = path_fmri + subjectID + "/ants/epi2braints.nii.gz"
    t1_file = "/shared/studies/nonregulated/connectome/Subjects/" + subjectID + \
            "/T1w/T1w_acpc_dc_restore_brain_2.00.nii.gz"
    if os.path.exists(reg_func_file) and os.path.exists(t1_file):

        try:
            reg_func = nibabel.load(reg_func_file)
            first_vol = image.index_img(reg_func, 0)
            t1 = nibabel.load(t1_file)

        except:
            print("{}: Error reading image".format(subjectID))
            continue

        struct = plotting.plot_anat(t1, title = subjectID)
        struct.add_edges(first_vol)
        struct.savefig("reports/" + subjectID + "/epi2struct.png")

        epi2struct = "reports/" + subjectID + "/epi2struct.png "
        subjects_as_string += epi2struct

    else:
        print("{}: Missing image".format(subjectID))

    #break

os.system("convert " + subjects_as_string + " reports/missing_subs_epi2struct.pdf")

