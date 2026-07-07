import base64
import hashlib

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.primitives.ciphers import algorithms, modes, Cipher
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization


def decrypt_session_key(encrypted_session_key_b64: str, private_key: RSAPrivateKey) -> bytes:
    encrypted_session_key_bytes = base64.b64decode(encrypted_session_key_b64)
    session_key = private_key.decrypt(encrypted_session_key_bytes,
                                      padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()), algorithm=hashes.SHA1(),
                                                   label=None))
    return session_key


def decrypt_payload(ciphertext_b64: str, session_key: bytes, iv_b64: str, algorithm: str) -> bytes:
    ciphertext_bytes = base64.b64decode(ciphertext_b64)
    iv = base64.b64decode(iv_b64)
    plaintext = None
    if algorithm == "AES":
        myCipher = Cipher(algorithms.AES(session_key), modes.CFB(iv))
        myDecryptor = myCipher.decryptor()
    else:  ##"3DES"
        myCipher = Cipher(algorithms.TripleDES(session_key), modes.CFB(iv))
        myDecryptor = myCipher.decryptor()

    plaintext = myDecryptor.update(ciphertext_bytes) + myDecryptor.finalize()
    return plaintext
