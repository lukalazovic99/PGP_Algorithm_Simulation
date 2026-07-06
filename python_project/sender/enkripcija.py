import os

from cryptography.hazmat.primitives.ciphers import algorithms, modes, Cipher
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

def enkriptuj(data:bytes,key,algoritam:str):
    if(algoritam=="AES"):
        Ks = os.urandom(16)
        IV = os.urandom(16)
        alg = algorithms.AES(Ks)
        mode = modes.CFB(IV)
    else: #alg je 3xDES
        Ks = os.urandom(24)
        IV = os.urandom(8)
        alg = algorithms.TripleDES(Ks)
        mode = modes.CFB(IV)

    nacin_sifrovanja = Cipher(alg,mode)
    sifra = nacin_sifrovanja.encryptor()
    EKs_MSG = sifra.update(data) + sifra.finalize()

    EPub_Ks = key.encrypt(
        Ks,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None
        )
    )

    return EPub_Ks, EKs_MSG, IV

