import subprocess
import os
import pandas as pd

def mp4_to_wav(src_dir, dest_dir, src_file, dest_file):
    wav_name = []
    mp4_file = pd.read_csv(src_file)
    for i in range(len(mp4_file['URL'])):
        try:
            input_file = src_dir+'/'+str(i)+'.mp4'
            output_file = dest_dir+'/'+str(i)+'.wav'
            subprocess.call(['ffmpeg', '-i', input_file, '-codec:a', 'pcm_s16le', '-ac', '1', output_file])
            if src_dir == dest_dir:
                os.system("rm "+input_file)
            wav_name.append(str(i)+'.wav')
        except:
            pass
    pd.DataFrame({"name": wav_name, "start_time": mp4_file['start_time'], "time_dur":mp4_file['time_dur']}).to_csv(dest_file, index=False, header=True)

def trim_wav(src_dir, dest_dir, src_file):
    wav_file = pd.read_csv(src_file)
    if not os.path.isdir(dest_dir):
        os.system("mkdir "+dest_dir)
    for i in range(len(wav_file['name'])):
        input_file = src_dir + '/' + wav_file['name'][i]
        output_file = dest_dir + '/' + wav_file['name'][i]
        start_t = str(wav_file['start_time'][i])
        time_dur = str(wav_file['time_dur'][i])
        os.system("ffmpeg -ss "+start_t+" -t "+time_dur+" -i "+input_file+" "+output_file)

# mp4_to_wav('dataset', 'dataset', 'down_list.csv', 'wav_files.csv')
trim_wav('dataset', 'clear_data', 'wav_files.csv')
