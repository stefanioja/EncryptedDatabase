"""This module provides utility functions for cryptographic operations.

Functions:
    get_size_in_bytes(n: int) -> int:
        Calculate the size in bytes required to represent an integer in binary.
    block_walk(src, dest, block_size, func) -> None:
        Process the source data in blocks and write the result to destination.
    pad(msg: bytes, key_len: int) -> bytes:
        Apply padding to a message.
    unpad(msg: bytes, key_len: int) -> tuple[bytes, int]:
        Remove padding from the message and return the unpadded message.
    base64_tuple(pair):
        Encode a pair of integers into base64 format as tuples.
"""

import os
import sys
import base64


def get_size_in_bytes(n: int) -> int:
    """Calculate the size in bytes required to represent an integer in binary.

    Arguments:
        n: The integer whose byte size is to be calculated.

    Returns:
        The size in bytes to represent the integer.
    """
    return (n.bit_length() + 7) // 8


def block_walk(src, dest, block_size, func) -> None:
    """Process the source data in blocks and write the result to destination.

    Arguments:
        src: The source file or buffer to read data from.
        dest: The destination file or buffer to write processed data to.
        block_size: The size of each block of data to be read and processed.
        func: The function to apply to each block of data.
    """
    while True:
        block = src.read(block_size)
        if not block:
            return

        dest.write(func(block))


def pad(msg: bytes, key_len: int) -> bytes:
    """Apply padding to a message.

    Arguments:
        msg: The message to be padded.
        key_len: The length of the key in bytes.

    Returns:
        The padded message.
    """
    start = b"\x00\x01"
    separator = b"\x02"

    padding_size = key_len - 1 - len(msg) - 3
    padding = bytearray(os.urandom(padding_size))

    for i in range(len(padding)):
        if padding[i] == 0:
            padding[i] = os.urandom(1)[0]

    padded_message = start + padding + separator + msg

    return padded_message


def unpad(msg: bytes, key_len: int) -> tuple[bytes, int]:
    """Remove padding from the message and return the unpadded message.

    Arguments:
        msg: The padded message.
        key_len: The length of the key in bytes.

    Returns:
        A tuple containing the unpadded message and the padding length.
    """
    pos = msg.find(b"\x02", 1)
    return msg[pos + 1:], (key_len - pos - 2)


def base64_tuple(pair):
    """Encode a pair of integers into base64 format as tuples.

    Arguments:
        pair: A tuple containing two integers to be encoded.

    Returns:
        A tuple containing the base64-encoded values of the integers.
    """
    return tuple(
        base64.b64encode(
            x.to_bytes(get_size_in_bytes(x), byteorder=sys.byteorder)
        )
        for x in pair
    )
