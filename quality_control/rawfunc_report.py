from init_reports_directory import subject_list, path_fmri
from nilearn import plotting, image
import nibabel
import os


subjects_as_string = ""
for subjectID in subject_list:

    if os.path.exists(path_fmri + subjectID + "/rawfunc.nii.gz"):

        try:
            img_file = path_fmri + subjectID + "/rawfunc.nii.gz"
            img = nibabel.load(img_file)
            vol = image.index_img(img, 3)
            if os.path.exists("reports/" + subjectID + "/rawfunc.png"):
                os.remove("reports/" + subjectID + "/rawfunc.png")
            plotting.plot_stat_map(vol, title = subjectID, 
                    bg_img = None, output_file = "reports/" + subjectID + "/rawfunc.png")

            rawfunc_file = "reports/" + subjectID + "/rawfunc.png "
            subjects_as_string += rawfunc_file

        except:
            print("{}: Error reading image".format(subjectID))

    else:
        print("{} missing rawfunc".format(subjectID))

    #break

os.system("convert " + subjects_as_string + " reports/missing_subs_rawfunc.pdf")

