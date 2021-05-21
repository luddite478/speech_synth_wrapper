import subprocess as sp
import sys
import time
import random
import requests
import dotenv
import os
import jwt
import re

dotenv.load_dotenv()

def balcon_voice_gen(lines):
	line = line.strip()
	pitch = random.randrange(-10, -9)
	for line in lines:
		cmd1 = 'balcon -t "{}" -n "Pavel" -p {} -w "output/{}".wav'.format(line,pitch,line)
		p = sp.call(cmd1, shell=True)

def yandex_get_iam_token(jwt_token):
	#jwt_token = os.getenv('jwt')
	yandex_url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
	get_iam_token_payload = { 'jwt': jwt_token }
	
	res = requests.post(yandex_url, json = get_iam_token_payload)
	if res.status_code == 200:
		return res.json()['iamToken']
	else:
		print('Can not get iam token', res.text)
		return ''

def yandex_synthesize(iam_token, text):
	if text == '':
		return

	url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
	headers = {
        'Authorization': 'Bearer ' + iam_token,
    }

	data = {
        'text': text,
        'lang': 'ru-RU',
        'folderId': os.getenv('yandex_folder_id')
    }
	
	with requests.post(url, headers=headers, data=data, stream=True) as resp:
		if resp.status_code != 200:
			raise RuntimeError("Invalid response received: code: %d, message: %s" % (resp.status_code, resp.text))
		
		for chunk in resp.iter_content(chunk_size=None):
			yield chunk

def yandex_create_jwt():
	service_account_id = os.getenv('yandex_service_acc_id')
	key_id = os.getenv('key_id') 

	with open("yandex_private.pem", 'r') as private:
		private_key = private.read()

	now = int(time.time())
	payload = {
			'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
			'iss': service_account_id,
			'iat': now,
			'exp': now + 360}

	encoded_token = jwt.encode(
		payload,
		private_key,
		algorithm='PS256',
		headers={'kid': key_id})

	dotenv.set_key("./.env", "jwt", encoded_token)
	
	return encoded_token



voice_src = "yandex"

if len(sys.argv) > 1:
	text = sys.argv[1]

file1 = open('input/a.txt', 'r', encoding='utf-8')
lines = file1.readlines()

if voice_src == "balcon":
	balcon_voice_gen(lines)

if voice_src == "yandex":
	jwt_token = yandex_create_jwt()
	iam_token = yandex_get_iam_token(jwt_token)

	for i, line in enumerate(lines):
		line = line.strip()
		line_number = str(i)
		file_name = line_number + "_" + re.sub(r'[^\w]', ' ', line).replace(' ', '_')
		
		output_file_path = os.path.abspath("output/{}.wav".format(file_name))
		with open(output_file_path, "w+b") as f:
			for audio_content in yandex_synthesize(iam_token, line):
				f.write(audio_content)



	