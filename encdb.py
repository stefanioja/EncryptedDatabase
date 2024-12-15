import json
import os
import sys
import argparse
import SCrypt.RSA as rsa
import db.dbconn as db
import sqlite3

if __name__ == '__main__':
    commander = argparse.ArgumentParser(prog='EncryptedDatabase', description='Tool to encrypt and manage files')
    subcommander = commander.add_subparsers(dest='command')

    read = subcommander.add_parser('read', description='decrypts a file from database')
    read.add_argument('-f', '--filename', help='name of the file to be decrypted', required=True, type=str)
    read.add_argument('-k', '--key', help='private key for decryption', required=True, type=str)
    read.add_argument('-o', '--output', help='file where the content will be stored', required=False, type=str)

    generate = subcommander.add_parser('generate', description='generates a new key pair')
    generate.add_argument('-d', '--default', help='updates the default key for the current user', required=False, action='store_true')
    generate.add_argument('-o', '--output', help='file where the keys will be stored', required=False, type=str)

    encrypt = subcommander.add_parser('encrypt', description='encrypt a file and adds it to the database')
    encrypt.add_argument('-f', '--filename', help='path of the file to be encrypted', required=True, type=str)
    encrypt.add_argument('-k', '--key', help='id of the public key used for decryption', required=False, type=int)

    delete = subcommander.add_parser('delete', description='deletes a file from the database')
    delete.add_argument('-f', '--filename', help='name of the file to be deleted', required=True, type=str)

    args = commander.parse_args()

    if args.command == 'read':
        args = read.parse_known_args()
    elif args.command == 'generate':
        args = generate.parse_known_args()
    elif args.command == 'encrypt':
        args = encrypt.parse_known_args()
    elif args.command == 'delete':
        args = delete.parse_known_args()
    else:
        commander.print_help()

    # with open('config.json', 'r') as fptr:
    #     config = json.loads(fptr.read())

    # try:
    #     key_len = config['key_length']
    #     db_path = config['db_path']
    #     if key_len < 64:
    #         print('key_length must be at least 64 bits long')
    # except KeyError as e:
    #     print(f"{e} is missing from config.json")

    # db.connect(db_path)

    # src = sys.argv[1]
    # dest = sys.argv[2]
    # restore = sys.argv[3]

    # public_key, private_key = rsa.RSA_key_gen(key_len) 
    # username = os.getlogin()
    # user = db.get_user_by_username(username)
    # if user is None:
    #     user_id = db.add_user(username)
    # else:
    #     user_id = user[0]

    # try:
    #     key_id = db.add_key(user_id, str(public_key[0]), str(public_key[1]))
    #     rsa.RSA_encrypt_file(src, dest, public_key)
    #     db.add_file(os.path.basename(src), dest, key_id, user_id)
    #     rsa.RSA_decrypt_file(dest, restore, private_key)
    # except sqlite3.IntegrityError:
    #     print(f'{src} is not unique')

    # db.disconnect()
