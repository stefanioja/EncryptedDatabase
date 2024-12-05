import random

def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """
    Computes the extended greatest common divisor of two numbers a and b,

    Arguments:
        a: first integer
        b: second integer

    Returns:
        A tuple (gcd, x, y) where:
        - gcd is the greatest common divisor of a and b
        - x and y are the coefficients satisfying a * x + b * y = gcd(a, b)
    """

    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def mod_inverse(a: int, n: int) -> int:
    """
    Calculates the modular inverse of a number a modulo n

    Arguments:
        a: The number for which the modular inverse needs to be calculated
        n: The modulus

    Returns:
        The result of (a ^ (-1)) mod n
    """
    _, x, _ = extended_gcd(a, n)
    return x % n
    
def modulo_exp(base: int, exp: int, m: int) -> int:
    """
    Modular exponentiation algorithm

    This implementation uses the Right-to-left binary methods for efficent computations

    Arguments:
        base: base
        exp: exponent
        m: modulus

    Returns:
        The result of (base ^ exp) mod m
    """
    if m == 1:
        return 0
    
    result = 1
    base = base % m
    while exp > 0: #iterates bits from right to left
        if exp % 2 == 1: #checks if the last bit of exp is 1
            result = (result * base) % m
        exp >>= 1
        base = (base * base) % m
    return result

def miller_rabin(n: int, k: int) -> bool:
    """
    Implemntation of Miller-Rabin primality test
    
    Arguments:
        n: number to be tested
        k: number of iterations

    Returns:
        True if n is prime (with high probability), False if n is composite
    """
    if n <= 1:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    m = n - 1
    s = 0

    while m % 2 == 0:
        s += 1
        m //= 2

    d = m

    for i in range(0, k):
        a = random.randint(2, n - 2)
        x = modulo_exp(a, d, n)

        for j in range(0, s):
            y = modulo_exp(x, 2, n)
            if y == 1 and x != 1 and x != n - 1:
                return False
        
            x = y
        
        if y != 1:
            return False
    
    return True

def prime_gen(size: int) -> int:
    """
    Generates a random prime number
    
    Arguments:
        size: size of the number to be generated (in bits)
        
    Returns:
        A prime number that needs <=size bits to be written
    """
    while True:
        p = random.randint(0, (1 << size) - 1)
        if miller_rabin(p, 5):
            break

    return p