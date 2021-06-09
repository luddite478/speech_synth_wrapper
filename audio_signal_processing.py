import subprocess as sp

def process_audio(input_file_path, audio_options, output_path):
	pitch_multiplier = audio_options['pitch']

	pitch_cmd = [
		'ffmpeg', '-hide_banner',
		'-f', 's16le',
		'-i', '-',
		'-af', 'asetrate=44100*{},aresample=44100,atempo=1/{}'.format(pitch_multiplier,pitch_multiplier), 
		output_path
	]

	resample_cmd = [
		'ffmpeg', 
		'-hide_banner', 
		'-f', 's16le', 
		'-ar', '48.0k', 
		'-ac', '1', 
		'-i', input_file_path, 
		'-sample_rate', '44100',
		'-y'
	] 

	del_tmp_file_cmd = [
		'&', 
		'DEL', 
		'/F', 
		input_file_path
	]

	cmd = resample_cmd + [ output_path ] + del_tmp_file_cmd

	# # concat commands 
	if pitch_multiplier != '1':
		resample_output = ['-f', 's16le', '-', '|']
		cmd = resample_cmd + resample_output + pitch_cmd + del_tmp_file_cmd

	print(cmd)
	sp.Popen(cmd, stderr=sp.PIPE, shell=True)
 
	print('\n')