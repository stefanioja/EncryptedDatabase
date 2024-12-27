import random
import sys
from math import gcd
from SCrypt.NT import prime_gen
from SCrypt.utils import *

def RSA_key_gen(key_len: int) -> tuple[tuple[int, int], tuple[int, int]]:
    """
    Generates a public and a private key for RSA encryption/decryption
    
    Arguments:
        key_len: length of the key in bits
        
    Returns:
        The tuple (public_key, private_key) with RSA keys
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

def RSA_encrypt(plaintext: bytes, public_key: tuple[int, int]) -> bytes:
    e = public_key[0]
    n = public_key[1]
    
    m = int.from_bytes(pad(plaintext, get_size_in_bytes(n)), byteorder=sys.byteorder)
    c = pow(m, e, n)

    ciphertext = c.to_bytes(get_size_in_bytes(n), byteorder=sys.byteorder)

    return ciphertext

def RSA_decrypt(ciphertext: bytes, private_key: tuple[int, int]) -> bytes:
    d = private_key[0]
    n = private_key[1]


    c = int.from_bytes(ciphertext, byteorder=sys.byteorder)
    m = pow(c, d, n)
    
    plaintext = m.to_bytes(get_size_in_bytes(m), byteorder=sys.byteorder)
    plaintext, plaintext_len = unpad(plaintext, get_size_in_bytes(n))
    
    plaintext += b'\x00' * (plaintext_len - len(plaintext))
    return plaintext

def RSA_encrypt_file(path_src: str, path_dest: str, public_key: tuple[int, int]) -> None:
    n = public_key[1]
    block_size = get_size_in_bytes(n) - 1 - 3
    
    block_walk(path_src, path_dest, block_size, RSA_encrypt, public_key)

def RSA_decrypt_file(path_src: str, path_dest: str, private_key: tuple[int, int]) -> None:
    n = private_key[1]
    block_size = get_size_in_bytes(n)

    block_walk(path_src, path_dest, block_size, RSA_decrypt, private_key)