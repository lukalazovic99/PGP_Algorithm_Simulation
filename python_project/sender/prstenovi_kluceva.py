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

