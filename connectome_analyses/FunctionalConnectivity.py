from sklearn.covariance import GraphLassoCV
import nibabel
import nilearn.regions
from nilearn.input_data import NiftiLabelsMasker
from nilearn.connectome import ConnectivityMeasure
import numpy as np


class FunctionalConnectome:

    def __init__(self, subjectID):
        self.subjectID = subjectID
        self.path_fmri = "/shared/studies/nonregulated/connectome/fmri/subjects/" + subjectID + "/"
        self.path_HCP = "/shared/studies/nonregulated/connectome/Subjects/" + subjectID + "/T1w/"

    def create_functional_connectivity_matrix(self):
        """ Performs functional connectivity analysis on a subject
            using temporal correlation and sparse inverse covariance
            of activity between brain regions across time
        """

        # Focus on signal only coming from voxels in grey matter
        regions = nibabel.load(self.path_HCP + 'GMmask_2.00.nii.gz')
        fmri4D = nibabel.load(self.path_fmri + '/denoise.ica/Denoised_data.nii.gz')
        nilearn.regions.img_to_signals_labels(fmri4D, regions)

        # Masks out the CSF signal, WM signal, and motion confounds
        masker = NiftiLabelsMasker(labels_img=regions, standardize=True,
                                   memory='nilearn_cache', verbose=5)
        time_series = masker.fit_transform(self.path_fmri + '/denoise.ica/Denoised_data.nii.gz',
                                           confounds=self.path_fmri + '/spreadsheets/all_confounds.csv')

        # Obtain functional connectivity matrix using full correlation
        correlation_measure = ConnectivityMeasure(kind='correlation')
        correlation_matrix = correlation_measure.fit_transform([time_series])[0]
        np.fill_diagonal(correlation_matrix, 0)
        with open(self.path_fmri + '/rsfmri_correl.csv', 'wb') as outfile:
            np.savetxt(outfile, correlation_matrix, delimiter=",")

        # Obtain the "partion correlation" matrix using sparse inverse covariance
        estimator = GraphLassoCV()
        estimator.fit(time_series)
        estimator.precision_
        estimator.precision_ = np.ma.array(-estimator.precision_)
        np.fill_diagonal(estimator.precision_, 0)
        with open(self.path_fmri + '/rsfmri_part_cor.csv', 'wb') as outfile:
            np.savetxt(outfile, estimator.precision_, delimiter=",")
