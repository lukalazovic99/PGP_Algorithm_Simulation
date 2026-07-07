from datetime import datetime

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from keys.prstenovi_kljuceva import *

def generisi_kljuceve(name:str,email:str,size:int,password:str):
    pr = rsa.generate_private_key(65537,size)
    pu = pr.public_key()


    javni = pu.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")


    privatni = pr.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.BestAvailableEncryption(password.encode("utf-8"))
    ).decode("utf-8")

    n = pu.public_numbers().n
    donjih_64_bita = n % (2 ** 64)  #(PUa mod 2^64)
    keyid= format(donjih_64_bita, "016X")


    privatni_dic = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "key_id": keyid,
        "user_name" : name,
        "user_email": email,
        "key_size": size,
        "public_key": javni,
        "encrypted_private_key": privatni
    }

    javni_dic = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), #mora ovaj strftime da bi stao u JSON
        "key_id": keyid,
        "user_name": name,
        "user_email": email,
        "key_size": size,
        "public_key": javni
    }


    dodaj_javni_kljuc(javni_dic)
    dodaj_privatni_kljuc(privatni_dic)


generisi_kljuceve("Bogdan","boki@nba.vr", 1024, "ipMANcar1234")
generisi_kljuceve("NAROD","pozlatiti@srb.vranje", 2048, "12345")
generisi_kljuceve("Anja Mihailov","cancel@bali.vr", 1024, "nonce")
generisi_kljuceve("Luka Skoko","meil@mail.mail", 2048, "wtf")
generisi_kljuceve("Drobi","mbape@diktator.mail", 1024, "12345")


