import json
import os
import SCrypt.RSA as rsa

with open('config.json', 'r') as fptr:
    config = json.loads(fptr.read())

try:
    key_len = config['key_length']
except KeyError as e:
    print(f"{e} is missing from config.json")
    os._exit(-1)

public_key, private_key = rsa.RSA_key_gen(key_len)