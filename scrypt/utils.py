import os
import sys
import base64


def get_size_in_bytes(n: int) -> int:
    return (n.bit_length() + 7) // 8


def block_walk(src, dest, block_size, func) -> None:
    while True:
        block = src.read(block_size)
        if not block:
            return

        dest.write(func(block))


def pad(msg: bytes, key_len: int) -> bytes:
    start = b'\x00\x01'
    separator = b'\x02'

    padding_size = key_len - 1 - len(msg) - 3
    padding = bytearray(os.urandom(padding_size))

    for i in range(len(padding)):
        if padding[i] == 0:
            padding[i] = os.urandom(1)[0]

    padded_message = start + padding + separator + msg

    return padded_message


def unpad(msg: bytes, key_len: int) -> tuple[bytes, int]:
    pos = msg.find(b'\x02', 1)

    return msg[pos + 1:], (key_len - pos - 2)


def base64_tuple(pair):
    return tuple(base64.b64encode(x.to_bytes(get_size_in_bytes(x), byteorder=sys.byteorder)) for x in pair)
