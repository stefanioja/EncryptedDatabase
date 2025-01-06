""""""
import random
import sympy


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
        if sympy.isprime(p):
            break

    return p
