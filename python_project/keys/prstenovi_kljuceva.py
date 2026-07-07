import json
from pathlib import Path
from cryptography.hazmat.primitives import serialization

KEYS_DIR = Path(__file__).resolve().parent
PUBLIC_RING_PATH = KEYS_DIR / "PUkeys.json"
PRIVATE_RING_PATH = KEYS_DIR / "PRkeys.json"

def load_prsten_javnih_kljuceva ():
    with PUBLIC_RING_PATH.open("r", encoding="utf-8") as file:
        lista_kljuceva = json.load(file)
    return lista_kljuceva

def load_prsten_privatnih_kljuceva ():
    with PRIVATE_RING_PATH.open("r", encoding="utf-8") as file:
        lista_kljuceva = json.load(file)
    return lista_kljuceva

def store_prsten_javnih_kljuceva (prsten:list):
    with PUBLIC_RING_PATH.open("w", encoding="utf-8") as file:
        json.dump(prsten,file,indent=2)

def store_prsten_privatnih_kljuceva (prsten:list):
    with PRIVATE_RING_PATH.open("r", encoding="utf-8") as file:
        json.dump(prsten,file,indent=2)

def dodaj_javni_kljuc (kljuc:dict):
    lista_kljuceva = load_prsten_javnih_kljuceva()
    lista_kljuceva.append(kljuc)
    store_prsten_javnih_kljuceva(lista_kljuceva)

def dodaj_privatni_kljuc (kljuc:dict):
    lista_kljuceva = load_prsten_privatnih_kljuceva()
    lista_kljuceva.append(kljuc)
    store_prsten_privatnih_kljuceva(lista_kljuceva)

def ukloni_javni_kljuc (id:str):
    lista_kljuceva = load_prsten_javnih_kljuceva()

    for kljuc in list(lista_kljuceva):
        if kljuc["key_id"]==id:
            lista_kljuceva.remove(kljuc)

    store_prsten_javnih_kljuceva(lista_kljuceva)

def ukloni_privatni_kljuc (id:str):
    lista_kljuceva = load_prsten_privatnih_kljuceva()

    for kljuc in list(lista_kljuceva):
        if kljuc["key_id"] == id:
            lista_kljuceva.remove(kljuc)

    store_prsten_privatnih_kljuceva(lista_kljuceva)

def dohvati_javni_kljuc(id:str):
    lista_kljuceva = load_prsten_javnih_kljuceva()

    for kljuc in list(lista_kljuceva):
        if kljuc["key_id"] == id:
            return kljuc

    return None

def dohvati_privatni_kljuc(id:str):
    lista_kljuceva = load_prsten_privatnih_kljuceva()

    for kljuc in list(lista_kljuceva):
        if kljuc["key_id"] == id:
            return kljuc

    return None

def dohvati_objekat_javni_kljuc(id:str):
    ke = dohvati_javni_kljuc(id)
    if ke is None:
        print("GRESKA dohvatanje javnog kljuca")
        return None
    ulaz_javnog_kljuca = ke["public_key"].encode("utf-8")
    pu_key = serialization.load_pem_public_key(ulaz_javnog_kljuca)
    return pu_key

def dohvati_objekat_privatni_kljuc(id:str,password:str):
    ke = dohvati_privatni_kljuc(id)
    if ke is None:
        print("GRESKA dohvatanje privatnog kljuca")
        return None
    ulaz_privatnog_kljuca = ke["encrypted_private_key"].encode("utf-8")
    try:
        pr_key = serialization.load_pem_private_key(ulaz_privatnog_kljuca, password.encode("utf-8"))
    except (ValueError, TypeError):
        print("GRESKA pogrešna lozinka")
        return None
    return pr_key

