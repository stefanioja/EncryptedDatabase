import os
import sqlite3

con = None
cursor = None

def connect(filepath: str) -> None:
    global con
    global cursor
    con = sqlite3.connect(filepath)
    cursor = con.cursor()

    dir = os.path.dirname(filepath)
    path = os.path.join(dir, 'db', 'schema.sql')
    with open(path, 'r') as reader:
        sql = reader.read()

    cursor.executescript(sql)
    con.commit()

def disconnect() -> None:
    global con, cursor
    print('disconnecting')
    cursor.close()
    con.close()

#CREATE
def add_user(username):
    global con, cursor
    cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
    id = cursor.lastrowid
    con.commit()
    
    return id

def add_key(user_id, e, n):
    global con, cursor
    cursor.execute("INSERT INTO keys (user_id, e, n) VALUES (?, ?, ?)", (user_id, e, n))
    id = cursor.lastrowid
    con.commit()

    return id

def add_file(filename, path, public_key_id, user_id):
    global con, cursor
    cursor.execute("INSERT INTO files (filename, path, public_key_id, user_id) VALUES (?, ?, ?, ?)", (filename, path, public_key_id, user_id))
    id = cursor.lastrowid
    con.commit()

    return id

#READ
def get_user_by_username(username):
    global con, cursor
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    return user

def get_key_by_key_id(key_id):
    global con, cursor
    cursor.execute("SELECT * FROM keys WHERE key_id = ?", (key,))
    key = cursor.fetchone()

    return key

def get_keys_by_user_id(user_id):
    global con, cursor
    cursor.execute("SELECT * FROM keys WHERE user_id = ?", (user_id,))
    key = cursor.fetchall()

    return key

def get_current_key_for_user(user_id):
    global con, cursor
    
    cursor.execute('SELECT k.* FROM users u JOIN keys k ON u.current_key_id = k.id WHERE u.id = ?', (user_id,))
    current_key = cursor.fetchone()
    
    return current_key

def get_file_by_filename(user_id, filename):
    global con, cursor
    cursor.execute('SELECT * FROM files WHERE user_id = ? and filename = ?', (user_id, filename))
    file = cursor.fetchone()

    return file

def get_files_by_user_id(user_id):
    global con, cursor
    cursor.execute("SELECT * FROM files WHERE user_id = ?", (user_id,))
    files = cursor.fetchall()

    return files

#UPDATE
def update_user(new_current_key_id, username):
    global con, cursor
    cursor.execute("UPDATE users SET current_key_id = ? WHERE username = ?", (new_current_key_id, username))
    con.commit()

#DELETE
def delete_user(username):
    global con, cursor
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    con.commit()

def delete_key(key_id):
    global con, cursor
    cursor.execute("DELETE FROM keys WHERE id = ?", (key_id,))
    con.commit()

def delete_file(user_id, filename):
    global con, cursor
    cursor.execute("DELETE FROM files WHERE user_id = ? and filename = ?", (user_id, filename))
    con.commit()
