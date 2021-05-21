import time
import jwt
import dotenv
import os

dotenv.load_dotenv()

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

