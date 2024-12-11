import json
import os
import SCrypt.RSA as rsa

enc = 'enc.jpeg'
dec = 'dec.jpeg'
if __name__ == '__main__':
    with open('config.json', 'r') as fptr:
        config = json.loads(fptr.read())

try:
    key_len = config['key_length']
    if key_len < 64:
        print('key_length must be at least 5 bytes long')
except KeyError as e:
    print(f"{e} is missing from config.json")

public_key, private_key = rsa.RSA_key_gen(key_len) 