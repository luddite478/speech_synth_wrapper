import requests
import os
from  audio_signal_processing import process_audio
import time
import dotenv
import jwt

script_dir = os.path.dirname(os.path.realpath(__file__))

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
    
    yandex_private = os.path.join(script_dir, "yandex_private.pem")
    with open(yandex_private, 'r') as private:
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
    
def parse_line_specific_args(line):
    synth_args_start_i = line.find("[")
    synth_args_end_i = line.find("]")

    if synth_args_start_i < 0 or synth_args_end_i < 0:
        return []

    synth_args_str = line[synth_args_start_i+1:synth_args_end_i]

    key_val_pairs = synth_args_str.split(',')
    
    line_args = {}
    for key_val in key_val_pairs:
        
        key, val = key_val.split('=')
        line_args[key] = val

    return line_args

def remove_line_specific_args(line):
    synth_args_start_i = line.find("[")
    synth_args_end_i = line.find("]")

    if synth_args_start_i > 0 or synth_args_end_i > 0:
        return line[0: synth_args_start_i:] + line[synth_args_end_i + 1::]
    else:
        return line

def delete_old_line_file_if_exists(line_num,output_path):
    processed_files = os.listdir(output_path)

    for p_file in processed_files:
        # line number if are first chars before first '_'
        line_num_processed_file = p_file.split('_')[0]

        if line_num == line_num_processed_file:
            os.remove(os.path.join(output_path,p_file))

def synthesize(iam_token, yandex_folder_id, text, synth_args, output_path):

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
    
    line_args = parse_line_specific_args(text)
    
    # Parse line args in square brackets ["v"="","e"="","s"="","l"="",p=""]
    voice     =  line_args["v"]    if  "v"    in  line_args else voice
    emotion   =  line_args["e"]    if  "e"    in  line_args else emotion
    speed     =  line_args["s"]    if  "s"    in  line_args else speed
    language  =  line_args["l"]    if  "l"    in  line_args else language
    pitch     =  line_args["p"]    if  "p"    in  line_args else '1'
    volume    =  line_args["vol"]  if  "vol"  in  line_args else '1'

    synth_args['voice']    = voice
    synth_args['emotion']  = emotion
    synth_args['speed']    = speed
    synth_args['language'] = language

    text      = remove_line_specific_args(text)
    ssml_text = convert_text_to_SSML(text)

    file_name_hash       = os.path.splitext(os.path.basename(output_path))[0]
    raw_folder_path      = os.path.join(script_dir, "raw")
    raw_file_output_path = os.path.join(raw_folder_path, file_name_hash + '.raw')

    # create folder for output audio
    with open(raw_file_output_path, "wb") as f:

        # request audio files   
        
        for audio_content in request_synth_data(yandex_folder_id, iam_token, ssml_text, synth_args):
            f.write(audio_content)
        f.close()
        print(text)
        
        audio_options = {
            'pitch': pitch,
            'volume': volume
        }

        process_audio(raw_file_output_path, audio_options, output_path)

    print('\n')


    


# python synth.py -i ./input/input.txt -o ./output

#request ->
#check cache for this line of text
# 1. if cache has this line return it 
# 2. if cache does not have it
#       