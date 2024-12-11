import os

def get_size_in_bytes(n: int) -> int:
    return (n.bit_length() + 7) // 8

def block_walk(path_src: str, path_dest: str, block_size: int, func, arg) -> None:
    with open(path_src, 'rb') as reader, open(path_dest, 'wb+') as writer:
        while True:
            block = reader.read(block_size)
            if not block:
                return
            
            writer.write(func(block, arg))

def pad(msg: bytes, key_len: int) -> bytes:
    start = b'\x00\x02'
    separator = b'\x00'
    
    padding_size = key_len - 1 - len(msg) - 3
    padding = bytearray(os.urandom(padding_size))

    for i in range(len(padding)):
        if padding[i] == 0:
            padding[i] = os.urandom(1)[0]  
    
    padded_message = start + padding + separator + msg

    return padded_message

def unpad(msg: bytes, key_len: int) -> tuple[bytes, int]:
    pos = msg.find(b'\x00', 2)
    
    return msg[pos + 1:], (key_len - pos - 2)
