import numpy as np
import pandas as pd
from sklearn import utils
import matplotlib
import librosa
import os
import preprocess.py
from sklearn.model_selection import train_test_split
from sklearn import svm
from sklearn import metrics
from sklearn.externals import joblib

# augment_driver('clear_data','aug_data', 20)

#extract_features(src_dir, src_file)
data = extract_features('clear_data2', 'wav_list.csv')

target = data['label']

# define outliers
outliers = target[target == -1]
nu = outliers.shape[0]/target.shape[0]


#remove labels before preparing testing and training data
data.drop(["label"], axis=1, inplace=True)

train_data, test_data, train_target, test_target = train_test_split(data, target, train_size = 0.8)

model = svm.OneClassSVM(nu=nu, kernel='rbf', gamma=0.0000005)
model.fit(train_data)

preds = model.predict(train_data)
targs = train_target

print("Training metrics: ")
print("accuracy: ", metrics.accuracy_score(targs, preds))
print("precision: ", metrics.precision_score(targs, preds))
print("recall: ", metrics.recall_score(targs, preds))
print("f1: ", metrics.f1_score(targs, preds))

preds = model.predict(test_data)
targs = test_target

print("Testing metrics: ")
print("accuracy: ", metrics.accuracy_score(targs, preds))
print("precision: ", metrics.precision_score(targs, preds))
print("recall: ", metrics.recall_score(targs, preds))
print("f1: ", metrics.f1_score(targs, preds))


# saving the trained model
outputfile = 'chain_saw_v1.model'
joblib.dump(model, outputfile, compress=9)
