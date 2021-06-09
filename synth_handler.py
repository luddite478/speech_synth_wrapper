import subprocess as sp
import random
import dotenv
import os
import yandex_synth
import shutil
import time

script_dir = os.path.dirname(os.path.realpath(__file__))
dotenv.load_dotenv()

def clear_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def balcon_voice_gen(lines):
	pitch = random.randrange(-10, -9)
	for line in lines:
		line = line.strip()
		cmd1 = 'balcon -t "{}" -n "Pavel" -p {} -w "output/{}".wav'.format(line,pitch,line)
		p = sp.call(cmd1, shell=True)


raw_folder_path = os.path.join(script_dir, "raw")

clear_folder(raw_folder_path)


def synthesize(request):
	
	backend  = request['backend']
	text     = request['text']
	output_path = request['output_path']
	backend  = request['backend']

	request.pop('backend', None)
	request.pop('id', None)
	synth_args = request

	if backend == "balcon":
		balcon_voice_gen(text)

	elif backend == "yandex":	
		yandex_folder_id = os.getenv('yandex_folder_id')
		last_token_gen_time = int(os.getenv('last_token_gen_time'))
		time_now = int(time.time())

		if (time_now - last_token_gen_time) > 10:
			jwt_token = yandex_synth.create_jwt()
			iam_token = yandex_synth.get_iam_token(jwt_token)
			dotenv.set_key("./.env", "last_token_gen_time", str(time_now))
		else:
			jwt_token = os.getenv('jwt')
			iam_token = os.getenv('iam_token')


		yandex_synth.synthesize(iam_token, yandex_folder_id, text, synth_args, output_path)

#python synth.py -b yandex -i input\input.txt -o Z:\sounds\railwaystation\2
