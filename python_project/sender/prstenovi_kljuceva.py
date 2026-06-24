import json


def load_prsten_javnih_kljuceva ():
    with open("PUkeys.json", "r") as file:
        lista_kljuceva = json.load(file)
    return lista_kljuceva

def load_prsten_privatnih_kljuceva ():
    with open("PRkeys.json", "r") as file:
        lista_kljuceva = json.load(file)
    return lista_kljuceva

def store_prsten_javnih_kljuceva (prsten:list):
    with open("PUkeys.json", "w") as file:
        json.dump(prsten,file)

def store_prsten_privatnih_kljuceva (prsten:list):
    with open("PRkeys.json", "w") as file:
        json.dump(prsten,file)

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

