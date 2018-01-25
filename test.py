from sklearn.externals import joblib
import subprocess

import numpy as np
import pandas as pd
from sklearn import utils
import matplotlib
import librosa
import os
from preproccess import prep_test


model = joblib.load('chain_saw_v1.model')

# test = prep_test('test_data/dog_3.mp3', '3.00')
# pred = model.predict(test)

if pred>0:
    print("Chainsaw")
else:
    print("Not Chainsaw")
