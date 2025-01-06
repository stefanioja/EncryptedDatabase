"""This module provides an implementation of RSA.

Functions:
    key_gen(key_len: int) -> tuple[tuple[int, int], tuple[int, int]]:
        Generates a public and a private key for RSA encryption/decryption.
    encrypt(plaintext: bytes, public_key: tuple[int, int]) -> bytes:
        Encrypts a plaintext message using the public RSA key.
    decrypt(ciphertext: bytes, private_key: tuple[int, int]) -> bytes:
        Decrypts a ciphertext message using the private RSA key.
    encrypt_file(path_src: str, path_dest: str, public_key: tuple[int,
        int]):
        Encrypts a file using the public RSA key.
    decrypt_file(path_src: str, path_dest: str, private_key: tuple[int,
        int]):
        Decrypts a file using the private RSA key.
"""

import random
import sys
import scrypt.utils as utils
from math import gcd
from scrypt.nt import prime_gen


def key_gen(key_len: int) -> tuple[tuple[int, int], tuple[int, int]]:
    """Generate a public and a private key for RSA encryption/decryption.

    Arguments:
        key_len: length of the key in bits.

    Returns:
        A tuple (public_key, private_key) containing RSA keys.
    """
    p = prime_gen(key_len // 2)
    q = prime_gen(key_len // 2)

    while p == q:
        p = prime_gen(key_len // 2)
        q = prime_gen(key_len // 2)

    n = p * q
    phi = (p - 1) * (q - 1)
    if phi > 65537:
        e = 65537
    elif phi > 17:
        e = 17
    else:
        e = 3

    if phi % e == 0:
        while gcd(e, phi) != 1:
            e = random.randint(2, phi - 1)

    d = pow(e, -1, phi)

    public_key = (e, n)
    private_key = (d, n)

    return public_key, private_key


def encrypt(plaintext: bytes, public_key: tuple[int, int]) -> bytes:
    """Encrypt a plaintext message using the public RSA key.

    Arguments:
        plaintext: The message to be encrypted.
        public_key: The public key (e, n) for RSA encryption.

    Returns:
        The encrypted ciphertext.
    """
    e = public_key[0]
    n = public_key[1]

    m = int.from_bytes(
        utils.pad(plaintext, utils.get_size_in_bytes(n)),
        byteorder=sys.byteorder,
    )
    c = pow(m, e, n)

    ciphertext = c.to_bytes(
        utils.get_size_in_bytes(n), byteorder=sys.byteorder
    )

    return ciphertext


def decrypt(ciphertext: bytes, private_key: tuple[int, int]) -> bytes:
    """Decrypt a ciphertext message using the private RSA key.

    Arguments:
        ciphertext: The encrypted message.
        private_key: The private key (d, n) for RSA decryption.

    Returns:
        The decrypted plaintext.
    """
    d = private_key[0]
    n = private_key[1]

    c = int.from_bytes(ciphertext, byteorder=sys.byteorder)
    m = pow(c, d, n)

    plaintext = m.to_bytes(utils.get_size_in_bytes(m), byteorder=sys.byteorder)
    plaintext, plaintext_len = utils.unpad(
        plaintext, utils.get_size_in_bytes(n)
    )

    plaintext += b"\x00" * (plaintext_len - len(plaintext))
    return plaintext


def encrypt_file(path_src: str, path_dest: str, public_key: tuple[int, int]):
    """Encrypt a file using the public RSA key.

    Arguments:
        path_src: The path to the source file to be encrypted.
        path_dest: The path to save the encrypted file.
        public_key: The public key (e, n) for RSA encryption.
    """
    n = public_key[1]
    block_size = utils.get_size_in_bytes(n) - 1 - 3

    with open(path_src, "rb") as src, open(path_dest, "wb+") as dest:
        utils.block_walk(
            src, dest, block_size, lambda x: encrypt(x, public_key)
        )


def decrypt_file(path_src: str, path_dest: str, private_key: tuple[int, int]):
    """Decrypt a file using the private RSA key.

    Arguments:
        path_src: The path to the encrypted source file.
        path_dest: The path to save the decrypted file, or None for stdout.
        private_key: The private key (d, n) for RSA decryption.
    """
    n = private_key[1]
    block_size = utils.get_size_in_bytes(n)

    def decrypt_func(x):
        return decrypt(x, private_key)

    with open(path_src, "rb") as src:
        if path_dest is not None:
            with open(path_dest, "wb+") as dest:
                utils.block_walk(src, dest, block_size, decrypt_func)
        else:
            utils.block_walk(src, sys.stdout.buffer, block_size, decrypt_func)
