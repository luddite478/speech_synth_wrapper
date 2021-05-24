import requests
import re
import os
import audio_reencode
import shutil
import time
import dotenv
import jwt


def get_iam_token(jwt_token):
	#jwt_token = os.getenv('jwt')
	yandex_url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
	get_iam_token_payload = { 'jwt': jwt_token }
	
	res = requests.post(yandex_url, json = get_iam_token_payload)
	if res.status_code == 200:
		return res.json()['iamToken']
	else:
		print('Can not get iam token', res.text)
		return ''

def create_jwt():
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

def convert_text_to_SSML(text):
    text = '<speak> ' + text + ' </speak>'

    # for i, ch in enumerate(text):
    #     # if ch == ',':
    #     #     text = text[:i+1] + ' <break strength="weak"> '   + text[i+1:]
    #     if ch == ':' or ch == ';' or ch == '-' or ch == '—':
    #         text = text[:i+1] + ' <break strength="medium"> ' + text[i+1:]
    #     elif ch == '.' or ch == '?' or ch == '!':
    #         text = text[:i+1] + ' <break strength="strong"> ' + text[i+1:]

    return text
    

def request_synth_data(folder_id, iam_token, ssml_text, synth_args):

    url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
    headers = {
        'Authorization': 'Bearer ' + iam_token,
    }
    print(synth_args['speed'])
    data = {
        'ssml': ssml_text,
        'voice': synth_args['voice'],
        'speed': synth_args['speed'],
        'emotion': synth_args['emotion'],
        'lang': synth_args['language'],
        'folderId': folder_id,
        'format': 'lpcm',
        'sampleRateHertz': 48000,
    }
    
    with requests.post(url, headers=headers, data=data, stream=True) as resp:
        if resp.status_code != 200:
            raise RuntimeError("Invalid response received: code: %d, message: %s" % (resp.status_code, resp.text))

        for chunk in resp.iter_content(chunk_size=None):
            yield chunk

def is_file_in_dir(file, dir):
    for _, dir, files in os.walk(dir):
        return file in files
    

def synthesize(iam_token, yandex_folder_id, text_file_path, synth_args, output_folder_path):

    # arguments or default values
    if synth_args['voice'] != None:
        voice = synth_args['voice']
    else:
        voice = 'oksana'

    if synth_args['emotion'] != None:
        emotion = synth_args['emotion']
    else:
        emotion = 'neutral'

    if synth_args['speed'] != None:
        speed = synth_args['speed']
    else:
        speed = '1.0'

    if synth_args['language'] != None:
        language = synth_args['language']
    else:
        language = 'ru-RU'   

    
    input_file = open(text_file_path, 'r', encoding='utf-8')
    lines = input_file.readlines()
    # iterate over lines in the text file

    # create folder for output audio
    final_output_path = os.path.join(output_folder_path,'[{}_{}_{}]'.format(voice,emotion,speed))
    if not os.path.exists(final_output_path):
        os.mkdir(final_output_path)
    
    for i, line in enumerate(lines):

        ssml_text = convert_text_to_SSML(line)
        print(ssml_text)

        line_number = str(i)
        file_name_text = re.sub(r'[^\w]', ' ', line).replace(' ', '_')
        file_name_text = file_name_text[:150] if len(file_name_text) > 150 else file_name_text
        # <text>_[<line_num>_<voice>_<emotion>_<speed>]
        file_name = file_name_text + "_" + "[{}_{}_{}_{}]".format(line_number,voice,emotion,speed) + '.raw'
        raw_file_output_path = os.path.join('raw', file_name)

        # create folder for output audio
        with open(raw_file_output_path, "wb") as f:
            # request audio files
            for audio_content in request_synth_data(yandex_folder_id, iam_token, ssml_text, synth_args):
                f.write(audio_content)
            f.close()
           
            audio_reencode.raw_to_wav(raw_file_output_path, final_output_path)


# python synth.py -i ./input/input.txt -o ./output