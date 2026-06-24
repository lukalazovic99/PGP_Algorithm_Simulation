from prstenovi_kljuceva import *

lista_kljuceva = load_prsten_javnih_kljuceva()

novikljuc = {
        "timestamp": "2026-06-23 14:30:00",
        "key_id": "MOJID",
        "user_id": "Bogdan bogdanNBA@vranje.vr",
        "key_size": "2048",
        "public_key": "-----BEGIN RSA PUBLIC KEY-----FAKEKEYDATA-----END RSA PUBLIC KEY-----"
    }
print(lista_kljuceva)

dodaj_javni_kljuc(novikljuc)#ovo snimi ali lista_kjuceva nije updated

lista_kljuceva = load_prsten_javnih_kljuceva()

print(lista_kljuceva)

print(dohvati_javni_kljuc("MOJID"))

ukloni_javni_kljuc("MOJID")

print(dohvati_javni_kljuc("MOJID"))