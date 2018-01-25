import numpy as np
import pandas as pd
from sklearn import utils
import matplotlib
import librosa
import os
import subprocess

from random import getrandbits
import sys, getopt, os

 # randomly turns on or off
def random_onoff():
    return bool(getrandbits(1))


# returns a list of augmented audio data, stereo or mono
def augment_data(y, sr, n_augment = 0, allow_speedandpitch = True, allow_pitch = True,
    allow_speed = True, allow_dyn = True, allow_noise = True, allow_timeshift = True, tab=""):

    mods = [y]                  # always returns the original as element zero
    length = y.shape[0]

    for i in range(n_augment):
        print(tab+"augment_data: ",i+1,"of",n_augment)
        y_mod = y
        count_changes = 0

        # change speed and pitch together
        if (allow_speedandpitch) and random_onoff():
            length_change = np.random.uniform(low=0.9,high=1.1)
            speed_fac = 1.0  / length_change
            print(tab+"    resample length_change = ",length_change)
            tmp = np.interp(np.arange(0,len(y),speed_fac),np.arange(0,len(y)),y)
            #tmp = resample(y,int(length*lengt_fac))    # signal.resample is too slow
            minlen = min( y.shape[0], tmp.shape[0])     # keep same length as original;
            y_mod *= 0                                    # pad with zeros
            y_mod[0:minlen] = tmp[0:minlen]
            count_changes += 1

        # change pitch (w/o speed)
        if (allow_pitch) and random_onoff():
            bins_per_octave = 24        # pitch increments are quarter-steps
            pitch_pm = 4                                # +/- this many quarter steps
            pitch_change =  pitch_pm * 2*(np.random.uniform()-0.5)
            print(tab+"    pitch_change = ",pitch_change)
            y_mod = librosa.effects.pitch_shift(y, sr, n_steps=pitch_change, bins_per_octave=bins_per_octave)
            count_changes += 1

        # change speed (w/o pitch),
        if (allow_speed) and random_onoff():
            speed_change = np.random.uniform(low=0.9,high=1.1)
            print(tab+"    speed_change = ",speed_change)
            tmp = librosa.effects.time_stretch(y_mod, speed_change)
            minlen = min( y.shape[0], tmp.shape[0])        # keep same length as original;
            y_mod *= 0                                    # pad with zeros
            y_mod[0:minlen] = tmp[0:minlen]
            count_changes += 1

        # change dynamic range
        if (allow_dyn) and random_onoff():
            dyn_change = np.random.uniform(low=0.5,high=1.1)  # change amplitude
            print(tab+"    dyn_change = ",dyn_change)
            y_mod = y_mod * dyn_change
            count_changes += 1

        # add noise
        if (allow_noise) and random_onoff():
            noise_amp = 0.005*np.random.uniform()*np.amax(y)
            if random_onoff():
                print(tab+"    gaussian noise_amp = ",noise_amp)
                y_mod +=  noise_amp * np.random.normal(size=length)
            else:
                print(tab+"    uniform noise_amp = ",noise_amp)
                y_mod +=  noise_amp * np.random.normal(size=length)
            count_changes += 1

        # shift in time forwards or backwards
        if (allow_timeshift) and random_onoff():
            timeshift_fac = 0.2 *2*(np.random.uniform()-0.5)  # up to 20% of length
            print(tab+"    timeshift_fac = ",timeshift_fac)
            start = int(length * timeshift_fac)
            if (start > 0):
                y_mod = np.pad(y_mod,(start,0),mode='constant')[0:y_mod.shape[0]]
            else:
                y_mod = np.pad(y_mod,(0,-start),mode='constant')[0:y_mod.shape[0]]
            count_changes += 1

        # last-ditch effort to make sure we made a change (recursive/sloppy, but...works)
        if (0 == count_changes):
            print("No changes made to signal, trying again")
            mods.append(  augment_data(y, sr, n_augment = 1, tab="      ")[1] )
        else:
            mods.append(y_mod)

    return mods

#driver function for making augmented data
def augment_driver(src_dir, dest_dir, n_augment):
    infile = os.listdir(src_dir)
    if not os.path.isdir(dest_dir):
        os.system("mkdir "+dest_dir)
    for file in infile:
        y, sr = librosa.load(src_dir+"/"+file, sr=None)
        mods = augment_data(y, sr, n_augment=n_augment)
        for i in range(len(mods)-1):
            outfile = dest_dir+"/"+file.split('.')[0]+"_aug"+str(i+1)+'.wav'
            print("      mod = ",i+1,": saving file",outfile,"...")
            librosa.output.write_wav(outfile,mods[i+1],sr)

"""
    Function extracts 5 types of features:
        1. MFCCs
        2. Mel spectograms
        3. chroma
        4. contrast
        5. tonnetz
"""
def extract_features(src_dir, src_file):
    src_list = pd.read_csv(src_file)
    mel_list = []
    mfcc_list = []
    chroma_list = []
    contrast_list = []
    tonnetz_list = []
    label = []
    ind = 0

    for name in src_list['name']:
        fname = src_dir + "/" + name
        try:

            X, sample_rate = librosa.load(fname, res_type='kaiser_fast')
            stft = np.abs(librosa.stft(X))

            mfccs = np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=40).T,axis=0)
            mfcc_list.append(mfccs)

            mel = np.mean(librosa.feature.melspectrogram(X, sr=sample_rate).T,axis=0)
            mel_list.append(mel)

            chroma = np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate).T,axis=0)
            chroma_list.append(chroma)

            contrast = np.mean(librosa.feature.spectral_contrast(S=stft, sr=sample_rate).T,axis=0)
            contrast_list.append(contrast)

            tonnetz = np.mean(librosa.feature.tonnetz(y=librosa.effects.harmonic(X), sr=sample_rate).T,axis=0)
            tonnetz_list.append(tonnetz)

            label.append(src_list['label'][int(name.split('.')[0])])

            ind+=1

            print(str(ind)+". "+fname + " processed.")

        except:
            pass

    df1 = {"mfcc_"+str(i):[mfcc_list[j][i] for j in range(ind)] for i in range(40)}
    df2 = {"mel_"+str(i):[chroma_list[j][i] for j in range(ind)] for i in range(12)}
    df3 = {"mel_"+str(i):[mel_list[j][i] for j in range(ind)] for i in range(128)}
    df4 = {"mel_"+str(i):[contrast_list[j][i] for j in range(ind)] for i in range(7)}
    df5 = {"mel_"+str(i):[tonnetz_list[j][i] for j in range(ind)] for i in range(6)}
    df6 = {"label":label}

    result = {}
    dicts = [df1, df2, df3, df4, df5,df6]
    for d in dicts:
        result.update(d)

    return pd.DataFrame(result)


# Prepare data for testing
def prep_test(fname, start_t):

    out_name = fname.split('.')[0]+'.wav'
    out_2name = out_name.split('.')[0]+'1.wav'
    subprocess.call(['ffmpeg', '-i', fname, '-codec:a', 'pcm_s16le', '-ac', '1', out_name])
    os.system("ffmpeg -ss "+start_t+" -t 4 -i "+out_name+" "+out_2name)

    X, sample_rate = librosa.load(out_2name, res_type='kaiser_fast')
    stft = np.abs(librosa.stft(X))

    mfccs = np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=40).T,axis=0)
    mel = np.mean(librosa.feature.melspectrogram(X, sr=sample_rate).T,axis=0)
    chroma = np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate).T,axis=0)
    contrast = np.mean(librosa.feature.spectral_contrast(S=stft, sr=sample_rate).T,axis=0)
    tonnetz = np.mean(librosa.feature.tonnetz(y=librosa.effects.harmonic(X), sr=sample_rate).T,axis=0)

    df1 = {"mfcc_"+str(i):[mfccs[i]] for i in range(40)}
    df2 = {"mel_"+str(i):[mel[i]] for i in range(128)}

    #modify df3, df4 and df5 to use all 193 features
    df3 = {"mel_"+str(i):[chroma[i]] for i in range(12)}
    df4 = {"mel_"+str(i):[contrast[i]] for i in range(7)}
    df5 = {"mel_"+str(i):[tonnetz[i]] for i in range(6)}

    result = {}
    dicts = [df1, df2, df3, df4, df5]
    for d in dicts:
        result.update(d)

    return pd.DataFrame(result)
