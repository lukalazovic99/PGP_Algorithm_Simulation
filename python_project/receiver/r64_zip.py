import base64
import zlib

def unzip(message):
    return zlib.decompress(message)

def decode_base64(message):
    return base64.b64decode(message)