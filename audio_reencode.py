import subprocess as sp
import os 

def raw_to_wav(input_file_path, output_folder_path):
	file_name = os.path.splitext(os.path.basename(input_file_path))[0]
	output_file_path = os.path.join(output_folder_path, file_name + '.wav')
	cmd = 'ffmpeg -hide_banner -f s16le -ar 48.0k -ac 1 -i "{}" -sample_rate 44100 -y "{}"'.format(input_file_path, output_file_path)

	sp.call(cmd, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)