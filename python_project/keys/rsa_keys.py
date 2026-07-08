from datetime import datetime

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from keys.prstenovi_kljuceva import *


def importuj_javni_kljuc(name: str, email: str, file_path: str):
    with open(file_path, "r", encoding="utf-8") as file:
        data = file.read()
    try:
        pu = serialization.load_pem_public_key(data.encode("utf-8")) #ovo se brine o tome da li je ispravan format
    except Exception:
        return {"ERROR": True, "info": "greska u .pem fajlu"}
    keyid = pu.public_numbers().n
    keyid = format(keyid%(2**64),"016X")
    size = pu.key_size

    javni_dic = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # mora ovaj strftime da bi stao u JSON
        "key_id": keyid,
        "user_name": name,
        "user_email": email,
        "key_size": size,
        "public_key": data
    }

    dodaj_javni_kljuc(javni_dic)
    return {"ERROR":False, "info": "importovan javni kljuc " + name}

def importuj_par_kljuceva(name: str, email: str, file_path: str):
    with open(file_path, "r", encoding="utf-8") as file:
        data = file.read()
    index = data.index("-----BEGIN ENCRYPTED PRIVATE KEY-----")
    pem_javnog = data[:index].strip()
    pem_privatnog = data[index:].strip()

    try:
        pu = serialization.load_pem_public_key(pem_javnog.encode("utf-8"))  # ovo se brine o tome da li je ispravan format
    except Exception:
        return {"ERROR": True, "info": "greska u .pem"}
    keyid = pu.public_numbers().n
    keyid = format(keyid % (2 ** 64), "016X")
    size = pu.key_size

    javni_dic = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # mora ovaj strftime da bi stao u JSON
        "key_id": keyid,
        "user_name": name,
        "user_email": email,
        "key_size": size,
        "public_key": pem_javnog
    }

    privatni_dic = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "key_id": keyid,  #imaju isti ID
        "user_name": name,
        "user_email": email,
        "key_size": size,
        "public_key": pem_javnog,
        "encrypted_private_key": pem_privatnog
    }

    dodaj_javni_kljuc(javni_dic)
    dodaj_privatni_kljuc(privatni_dic)

    return{"ERROR":False, "info": "importovan par kljuceva " + name}

def exportuj_par_kljuceva(key_id: str, file_path: str):
    pr = dohvati_privatni_kljuc(key_id)
    if pr is None:
        return {"ERROR": True, "info": "Kljuc nije pronadjen"}

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(pr["public_key"])
        file.write(pr["encrypted_private_key"])

    return {"ERROR": False, "info": "Par kljuceva uspesno eksportovan"}

def exportuj_javni_kljuc(key_id: str, file_path: str):
    pu = dohvati_javni_kljuc(key_id)
    if pu is None:
        return {"ERROR": True, "info": "Kljuc nije pronadjen"}

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(pu["public_key"])

    return {"ERROR": False, "info": "Javni kljuc uspesno eksportovan"}

def generisi_kljuceve(name: str, email: str, size: int, password: str):
    pr = rsa.generate_private_key(65537, size)
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
    donjih_64_bita = n % (2 ** 64)  # (PUa mod 2^64)
    keyid = format(donjih_64_bita, "016X")

    privatni_dic = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "key_id": keyid,
        "user_name": name,
        "user_email": email,
        "key_size": size,
        "public_key": javni,
        "encrypted_private_key": privatni
    }

    javni_dic = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # mora ovaj strftime da bi stao u JSON
        "key_id": keyid,
        "user_name": name,
        "user_email": email,
        "key_size": size,
        "public_key": javni
    }

    dodaj_javni_kljuc(javni_dic)
    dodaj_privatni_kljuc(privatni_dic)


#generisi_kljuceve("BogdanVlajinac","boki@nba.vr", 1024, "ipMANcar1234")

#generisi_kljuceve("NAROD","pozlatiti@srb.vranje", 2048, "12345")

#generisi_kljuceve("kljuc_anja","cancel@bali.vr", 1024, "nonce")

#generisi_kljuceve("kljuc_luka","meil@mail.mail", 2048, "wtf")

#generisi_kljuceve("DrobiKey","mbape@diktator.mail", 1024, "12345")

