import subprocess as sp
import argparse
import random
import dotenv
import os
import yandex_synth

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
	line = line.strip()
	pitch = random.randrange(-10, -9)
	for line in lines:
		cmd1 = 'balcon -t "{}" -n "Pavel" -p {} -w "output/{}".wav'.format(line,pitch,line)
		p = sp.call(cmd1, shell=True)

clear_folder('./raw')

voice_src = "yandex"

parser = argparse.ArgumentParser()
parser.add_argument("-b", "--backend",  required=True, help="IAM token")
parser.add_argument("-i", "--input",    required=True, help="input text path")
parser.add_argument("-v", "--voice",    required=False, help="voice")
parser.add_argument("-e", "--emotion",  required=False, help="emotion") 
parser.add_argument("-s", "--speed",    required=False, help="speed") 
parser.add_argument("-l", "--language", required=False, help="language")
parser.add_argument("-o", "--output",   required=True, help="Output file name")

args = parser.parse_args()

yandex_folder_id = os.getenv('yandex_folder_id')
backend = args.backend

if backend == "backend":
	balcon_voice_gen(lines)

elif backend == "yandex":
	jwt_token = yandex_synth.create_jwt()
	iam_token = yandex_synth.get_iam_token(jwt_token)
	text_file_path = args.input
	output_folder_path = args.output
	synth_args = vars(args)
	synth_args.pop('backend', None)
	yandex_synth.synthesize(iam_token, yandex_folder_id, text_file_path, synth_args, output_folder_path)

else:
	print('set backned')



	