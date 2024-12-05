from SCrypt.NT import prime_gen, mod_inverse

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

    n = p * q
    phi = (p - 1) * (q - 1)
    if phi > 65537:
        e = 65537
    else:
        e = 3

    d = mod_inverse(e, phi)

    public_key = (e, n)
    private_key = (d, n)

    return public_key, private_key