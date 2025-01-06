import json
import os
import sys
import base64
import argparse
import re
import sqlite3
import SCrypt.RSA as rsa
import SCrypt.utils as utils
import db.dbconn as db


def failure(msg, db):
    print(msg)
    if db is not None:
        db.disconnect()
    os._exit(-1)


def file_print(msg, path):
    if path is None:
        print(msg)
    else:
        try:
            with open(path, 'a+') as writer:
                writer.write(f'{msg}\n')
        except (FileNotFoundError, PermissionError):
            failure(f"couldn't write in file {args.output}", db)


if __name__ == '__main__':
    commander = argparse.ArgumentParser(
        prog='EncryptedDatabase', description='Tool to encrypt and manage files')
    subcommander = commander.add_subparsers(dest='command')

    read = subcommander.add_parser(
        'read', description='decrypts a file from database')
    read.add_argument(
        '-f', '--filename', help='name of the file to be decrypted', required=True, type=str)
    read.add_argument(
        '-k', '--key', help='private key for decryption', required=True, type=str)
    read.add_argument(
        '-o', '--output', help='file where the content will be stored', required=False, type=str)

    generate = subcommander.add_parser(
        'generate', description='generates a new key pair')
    generate.add_argument(
        '-d', '--default', help='updates the default key for the current user', required=False, action='store_true')
    generate.add_argument(
        '-o', '--output', help='file where the keys will be stored', required=False, type=str)

    encrypt = subcommander.add_parser(
        'encrypt', description='encrypt a file and adds it to the database')
    encrypt.add_argument(
        '-f', '--filepath', help='path of the file to be encrypted', required=True, type=str)
    encrypt.add_argument(
        '-k', '--key', help='id of the public key used for decryption', required=False, type=int)

    delete = subcommander.add_parser(
        'delete', description='deletes a file from the database')
    delete.add_argument(
        '-f', '--filename', help='name of the file to be deleted', required=True, type=str)

    account = subcommander.add_parser(
        'account', description='helps view and manage data linked to your account')
    account.add_argument('-f', '--files', help='show files',
                         action='store_true', required=False)
    account.add_argument('-k', '--keys', help='shows keys',
                         action='store_true', required=False)
    account.add_argument(
        '-d', '--default', help='updates the default key for the current user', required=False, type=int)
    account.add_argument(
        '-o', '--output', help='file where the output will be stored', required=False, type=str)

    args = commander.parse_args()

    abs_path = os.path.abspath(__file__)
    parent_dir = os.path.dirname(abs_path)

    try:
        with open(os.path.join(parent_dir, 'config.json'), 'r') as fptr:
            config = json.loads(fptr.read())
    except FileNotFoundError:
        failure('config.json not found', None)

    try:
        db_path = config['db_path']
    except KeyError as e:
        failure(f'{e} is missing from config.json', None)

    try:
        db.connect(os.path.join(parent_dir, db_path))
    except FileNotFoundError:
        failure('database schema not found', None)
    except sqlite3.Error:
        failure('database connection failed', None)

    username = os.getlogin()
    user = db.get_user_by_username(username)

    if user is None:
        user_id = db.add_user(username)
    else:
        user_id = user[0]

    if args.command == 'read':
        filename = args.filename
        key = args.key
        output = args.output

        file = db.get_file_by_filename(user_id, filename)
        if file is None:
            failure('file not found', db)

        path = file[2]

        key.strip('()')
        regex = r"(\S+)[, ]+(\S+)"
        match = re.match(regex, key)
        if match:
            key = (match.group(1), match.group(2))
        else:
            failure('invalid key format', db)

        d = int.from_bytes(base64.b64decode(key[0]), byteorder=sys.byteorder)
        n = int.from_bytes(base64.b64decode(key[1]), byteorder=sys.byteorder)
        key = (d, n)
        try:
            rsa.RSA_decrypt_file(path, output, key)
        except FileNotFoundError:
            failure(f'{path} not found', db)
    elif args.command == 'generate':
        try:
            key_len = config['key_length']
        except KeyError as e:
            failure(f"{e} is missing from config.json")

        public_key, private_key = rsa.RSA_key_gen(key_len)
        public_key = utils.base64_tuple(public_key)
        private_key = utils.base64_tuple(private_key)

        key_id = db.add_key(user_id, public_key[0], public_key[1])
        if args.default:
            db.update_user(key_id, user_id)

        e = public_key[0].decode('ascii')
        d = private_key[0].decode('ascii')
        n = private_key[1].decode('ascii')

        key_pair = f'({e}, {n})\n({d}, {n})'

        if args.output is not None:
            with open(args.output, 'w+') as writer:
                writer.write(key_pair)
        else:
            print(key_pair)
    elif args.command == 'encrypt':
        try:
            encrypted_path = config['encrypted_path']
        except Exception as e:
            failure(f"{e} is missing from config.json")

        filepath = args.filepath
        key = args.key

        if key is None:
            key = db.get_current_key_for_user(user_id)
            if key is None:
                failure("provide a key id or set a default one", db)
        else:
            key = db.get_key_by_key_id(key)
            if key is None:
                failure("provide a key id or set a default one", db)

        key_id = key[0]
        e = int.from_bytes(base64.b64decode(key[2]), byteorder=sys.byteorder)
        n = int.from_bytes(base64.b64decode(key[3]), byteorder=sys.byteorder)
        key = (e, n)
        rsa.RSA_encrypt_file(filepath, os.path.join(encrypted_path, os.path.basename(
            filepath)), key)  # aici da fail daca encrypted_path nu exista -> rezolva
        db.add_file(os.path.basename(filepath), os.path.join(
            encrypted_path, os.path.basename(filepath)), key_id, user_id)
    elif args.command == 'delete':
        filename = args.filename
        file = db.get_file_by_filename(user_id, filename)
        if file is None:
            failure('file not found', db)

        db.delete_file(user_id, filename)
        path = file[2]

        try:
            os.remove(path)
        except OSError as e:
            failure(f"File located at {path} can't be removed", db)
    elif args.command == 'account':
        output = args.output
        if args.files:
            files = db.get_files_by_user_id(user_id)

            for file in files:
                file_print(f'id: {file[0]}, filename: {file[1]}, dir: {
                           os.path.dirname(file[2])}, key_id: {file[3]}', output)

        if args.keys:
            keys = db.get_keys_by_user_id(user_id)
            for key in keys:
                file_print(f'id: {key[0]}, e: {key[2]}, n: {key[3]}', output)

        if args.default is not None:
            key_id = args.default
            key = db.get_key_by_key_id(key_id)
            if key is None:
                failure(f"key {key_id} wasn't found in the db", db)
            db.update_user(key_id, user_id)
    else:
        commander.print_help()

    db.disconnect()
