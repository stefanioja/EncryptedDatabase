import json
import os
import sys
import SCrypt.RSA as rsa
import db.dbconn as db
import sqlite3

if __name__ == '__main__':
    with open('config.json', 'r') as fptr:
        config = json.loads(fptr.read())

    try:
        key_len = config['key_length']
        db_path = config['db_path']
        if key_len < 64:
            print('key_length must be at least 64 bits long')
    except KeyError as e:
        print(f"{e} is missing from config.json")

    db.connect(db_path)

    src = sys.argv[1]
    dest = sys.argv[2]
    restore = sys.argv[3]

    public_key, private_key = rsa.RSA_key_gen(key_len) 
    username = os.getlogin()
    user = db.get_user_by_username(username)
    if user is None:
        user_id = db.add_user(username)
    else:
        user_id = user[0]

    try:
        key_id = db.add_key(user_id, str(public_key[0]), str(public_key[1]))
        rsa.RSA_encrypt_file(src, dest, public_key)
        db.add_file(os.path.basename(src), dest, key_id, user_id)
        rsa.RSA_decrypt_file(dest, restore, private_key)
    except sqlite3.IntegrityError:
        print(f'{src} is not unique')

    db.disconnect()
