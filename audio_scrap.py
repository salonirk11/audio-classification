from pytube import YouTube
import pandas as pd
import os
import subprocess


# to enlist all files with required links and data. /m/o1j4z9 corresponds to chainsaw sound label
def video_down_all(file_name):
	i=0
	for u in file_name['# YTID']:
		url_list.append(url+str(u))
		start_time.append(file_name[' start_seconds'][i])
		time_dur.append(file_name[' end_seconds'][i]-file_name[' start_seconds'][i])
		if '/m/01j4z9' in file_name[' positive_labels'][i].split(','):
			label.append(1)
		else:
			label.append(-1)
		i+=1

# to enlist only chainsaw videos
def video_down_saw(file_name):
    i=0
    for u in file_name['# YTID']:
        if '/m/01j4z9' in file_name[' positive_labels'][i].split(','):
        	url_list.append(url+str(u))
        	start_time.append(file_name[' start_seconds'][i])
        	time_dur.append(file_name[' end_seconds'][i]-file_name[' start_seconds'][i])
        	label.append(1)
        i+=1

# download videos enlisted in down_list
def down(down_list):
    d_det = pd.read_csv(down_list)
    for j in range(len(d_det['URL'])):
        try:
            yt = YouTube(d_det['URL'][i])
            yt.streams.filter(only_audio=True).first().download(output_path = 'dataset/', filename = str(i))
            print(str(i)+'.mp4 downloaded.')
        except :
            pass

#convert downloaded videos to .wav format
def mp4_to_wav(src_dir, dest_dir, src_file, dest_file):
    wav_name = []
	wav_start = []
	wav_dur = []
	wav_lab = []
    mp4_file = pd.read_csv(src_file)
    for name in file_list:
        try:
			i = int(name.split('.')[0])
            input_file = src_dir+'/'+str(i)+'.mp4'
            output_file = dest_dir+'/'+str(i)+'.wav'
			if not os.path.isdir(dest_dir):
		        os.system("mkdir "+dest_dir)

            subprocess.call(['ffmpeg', '-i', input_file, '-codec:a', 'pcm_s16le', '-ac', '1', output_file])
			print(output_file+" converted.")
            if src_dir == dest_dir:
                os.system("rm "+input_file)

            wav_name.append(str(i)+'.wav')
			wav_start.append(mp4_file['start_time'][i])
    		wav_dur.append(mp4_file['time_dur'][i])
    		wav_lab.append(mp4_file['label'][i])

        except:
            pass

    pd.DataFrame({"name": wav_name, "start_time": wav_start, "time_dur":wav_dur, "label": wav_lab}).to_csv(dest_file, index=False, header=True)

#trim .wav to 4s clips
def trim_wav(src_dir, dest_dir, src_file):
    wav_file = pd.read_csv(src_file)
    if not os.path.isdir(dest_dir):
        os.system("mkdir "+dest_dir)
    for i in range(len(wav_file['name'])):
        input_file = src_dir + '/' + wav_file['name'][i]
        output_file = dest_dir + '/' + wav_file['name'][i]
        start_t = str(wav_file['start_time'][i])
        os.system("ffmpeg -ss "+start_t+" -t 4 -i "+input_file+" "+output_file)
		print(output_file+" trimmed.")


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



url='https://youtu.be/'

eval_file = pd.read_csv('data/eval_segments.csv')
bal_train_file = pd.read_csv('data/balanced_train_segments.csv')
unbal_train_file = pd.read_csv('data/unbalanced_train_segments.csv')

url_list = []
start_time = []
time_dur = []
label = []

video_down_all(eval_file)
video_down_all(bal_train_file)
video_down_saw(unbal_train_file)

pd.DataFrame({"URL": url_list, "start_time": start_time, "time_dur":time_dur, "label":label}).to_csv('down_list.csv', index=False, header=True)

down('down_list.csv')

mp4_to_wav('dataset', 'dataset', 'down_list.csv', 'wav_files.csv')
trim_wav('dataset', 'clear_data', 'wav_files.csv')
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

video_down(eval_file)
video_down(bal_train_file)
# video_down(bal_train_file)

pd.DataFrame({"URL": url_list, "start_time": start_time, "time_dur":time_dur}).to_csv('down_list.csv', index=False, header=True)

down()
