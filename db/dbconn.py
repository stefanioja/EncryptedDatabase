"""This module provides functions to manage users, keys, and files in a db.

Functions:
    connect(filepath: str): Creates a connection to the database and a cursor.
    disconnect(): Closes the database connection and cursor.
    add_user(username: str) -> int: Creates an entry in the user table.
    add_key(user_id: int, e: int, n: int) -> int: Creates an entry in the keys.
    add_file(filename: str, path: str,
        public_key_id: int, user_id: int) -> int:
        Creates a new entry in the files table.
    get_user_by_username(username: str) -> tuple[int, str, str] | None:
        Retrieves a user by their username.
    get_key_by_key_id(key_id: int) -> tuple[int, int, str, str] | None:
        Retrieves a key from the database by its id.
    get_keys_by_user_id(user_id: int) -> list[tuple[int, int, str, str]]:
        Retrieves all keys associated with a user.
    get_current_key_for_user(user_id: int) -> tuple[int, int, str, str] | None:
        Retrieves the current default key for a user.
    get_file_by_filename(user_id: int, filename: str)
        -> tuple[int, str, str, int, int] | None:
        Retrieves a file record by filename for a user.
    get_files_by_user_id(user_id: int) -> list[tuple[int, str, str, int, int]]:
        Retrieves all files associated with a user.
    update_user(new_current_key_id: int, user_id: int):
        Changes the default public key for a user.
    delete_user(user_id: int): Deletes an entry in the users table.
    delete_key(key_id: int): Deletes an entry in the keys table.
    delete_file(user_id: int, filename: str):
        Deletes an entry in the files table.
"""

import os
import sqlite3

con = None
cursor = None


def connect(filepath: str):
    """Create a connection to the database and a cursor associated with it.

    If the database doesn't exist, the function creates it.
    This function must be called before any other functions from this module.

     Args:
        filepath: path to the SQLite database file.
    """
    global con
    global cursor
    con = sqlite3.connect(filepath)
    cursor = con.cursor()

    dir = os.path.dirname(filepath)
    path = os.path.join(dir, "db", "schema.sql")
    with open(path, "r") as reader:
        sql = reader.read()

    cursor.executescript(sql)
    con.commit()


def disconnect():
    """Close the database connection and cursor."""
    global con, cursor
    cursor.close()
    con.close()


# CREATE
def add_user(username: str) -> int:
    """Create an entry in the user table.

    Args:
        username: the username of the user to be added.

    Returns:
        The id of the new user.
    """
    global con, cursor
    cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
    id = cursor.lastrowid
    con.commit()
    return id


def add_key(user_id: int, e: int, n: int) -> int:
    """Create an entry in the keys table.

    Args:
        user_id: the id of the user to whom the key belongs.
        e: the exponent of the public key.
        n: the modulus of the public key.

    Returns:
        the id of the new key.
    """
    global con, cursor
    cursor.execute(
        "INSERT INTO keys (user_id, e, n) VALUES (?, ?, ?)", (user_id, e, n)
    )
    id = cursor.lastrowid
    con.commit()
    return id


def add_file(
    filename: str, path: str, public_key_id: int, user_id: int
) -> int:
    """Create a new entry in the files table.

    Args:
        filename: the name of the file.
        path: the path where the file is stored.
        public_key_id: the id of the associated public key.
        user_id: the id of the user who owns the file.

    Returns:
        the id of the new file.
    """
    global con, cursor
    cursor.execute(
        """INSERT INTO files
                   (filename, path, public_key_id, user_id)
                   VALUES (?, ?, ?, ?)""",
        (filename, path, public_key_id, user_id),
    )
    id = cursor.lastrowid
    con.commit()
    return id


# READ
def get_user_by_username(username: str) -> tuple[int, str, str] | None:
    """Retrieve a user from the database by their username.

    Args:
        username: the username of the user to be fetched.

    Returns:
        the user record, or None if the user is not found.
    """
    global con, cursor
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    return user


def get_key_by_key_id(key_id: int) -> tuple[int, int, str, str] | None:
    """Retrieve a key from the database by its id.

    Args:
        key_id: The id of the key to be fetched.

    Returns:
        the key record, or None if the key is not found.
    """
    global con, cursor
    cursor.execute("SELECT * FROM keys WHERE id = ?", (key_id,))
    key = cursor.fetchone()
    return key


def get_keys_by_user_id(user_id: int) -> list[tuple[int, int, str, str]]:
    """Retrieve all keys associated with a user from the database.

    Args:
        user_id: The id of the user whose keys are to be fetched.

    Returns:
        a list of key records, or an empty list if no keys are found.
    """
    global con, cursor
    cursor.execute("SELECT * FROM keys WHERE user_id = ?", (user_id,))
    key = cursor.fetchall()
    return key


def get_current_key_for_user(user_id: int) -> tuple[int, int, str, str] | None:
    """Retrieve the current default key for a user.

    Args:
        user_id: The id of the user whose current default key is to be fetched.

    Returns:
        a key record, or None if the key is not found.
    """
    global con, cursor
    cursor.execute(
        """SELECT k.* FROM users u
                   JOIN keys k ON u.current_key_id = k.id
                   WHERE u.id = ?""",
        (user_id,),
    )
    current_key = cursor.fetchone()
    return current_key


def get_file_by_filename(
    user_id: int, filename: str
) -> tuple[int, str, str, int, int] | None:
    """Retrieve a file record by filename for a specific user.

    Args:
        user_id: the id of the user who owns the file.
        filename: the name of the file to be fetched.

    Returns:
        a file record, or None if the file is not found.
    """
    global con, cursor
    cursor.execute(
        "SELECT * FROM files WHERE user_id = ? and filename = ?",
        (user_id, filename),
    )
    file = cursor.fetchone()
    return file


def get_files_by_user_id(user_id: int) -> list[tuple[int, str, str, int, int]]:
    """Retrieve all files associated with a user.

    Args:
        user_id: the id of the user whose files are to be fetched.

    Returns:
        a list of file records, or an empty list if no files are found.
    """
    global con, cursor
    cursor.execute("SELECT * FROM files WHERE user_id = ?", (user_id,))
    files = cursor.fetchall()
    return files


# UPDATE
def update_user(new_current_key_id: int, user_id: int):
    """Change the default public key for a specified user.

    Arguments:
        user_id: the id of the user who made the request.
        new_current_key_id: the id of the new default public key.
    """
    global con, cursor
    cursor.execute(
        "UPDATE users SET current_key_id = ? WHERE id = ?",
        (new_current_key_id, user_id),
    )
    con.commit()


# DELETE
def delete_user(user_id):
    """Delete an entry in the keys table.

    Arguments:
        user_id: the id of the user to be deleted.
    """
    global con, cursor
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    con.commit()


def delete_key(key_id: int):
    """Delete an entry in the keys table.

    Arguments:
        key_id: the id of the key to be deleted.
    """
    global con, cursor
    cursor.execute("DELETE FROM keys WHERE id = ?", (key_id,))
    con.commit()


def delete_file(user_id: int, filename: str):
    """Delete an entry in the files table.

    Arguments:
        user_id: the id of the user who made the request.
        filename: the name of the file to be deleted.
    """
    global con, cursor
    cursor.execute(
        "DELETE FROM files WHERE user_id = ? and filename = ?",
        (user_id, filename),
    )
    con.commit()
