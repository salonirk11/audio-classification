from pytube import YouTube
import pandas as pd
import os

url='https://youtu.be/'

eval_file = pd.read_csv('eval_segments.csv')
bal_train_file = pd.read_csv('balanced_train_segments.csv')
# unbal_train_file = pd.read_csv('audioset_v1_embeddings/unbalanced_train_segments.csv')

url_list = []
start_time = []
time_dur = []

def video_down(file_name):
    i=0
    for u in file_name['# YTID']:
        if '/m/01j4z9' in file_name[' positive_labels'][i].split(','):
            url_list.append(url+str(u))
            start_time.append(file_name[' start_seconds'][i])
            time_dur.append(file_name[' end_seconds'][i]-file_name[' start_seconds'][i])
        i+=1

def down():
    d_det = pd.read_csv('down_list.csv')
    for i in range(23,len(d_det['URL'])):
        try:
            yt = YouTube(d_det['URL'][i])
            yt.streams.filter(only_audio=True).first().download(output_path = 'dataset/', filename = str(i))
            print(str(i)+'.mp4 downloaded.')
        except:
            pass

video_down(eval_file)
video_down(bal_train_file)
# video_down(bal_train_file)

pd.DataFrame({"URL": url_list, "start_time": start_time, "time_dur":time_dur}).to_csv('down_list.csv', index=False, header=True)

down()
