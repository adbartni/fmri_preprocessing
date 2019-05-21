import os
import subprocess
from __init__ import fslDir
from Preprocessing import Preprocessing


class StructuralProcessing(Preprocessing):

    def __init__(self):
        self.subjectID = Preprocessing.subjectID