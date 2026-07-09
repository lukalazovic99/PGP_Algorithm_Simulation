import base64
import zlib
import json
from cryptography.hazmat.primitives import serialization
from keys.prstenovi_kljuceva import *
from sender.enkripcija import enkriptuj
from sender.potpis import potpisi_poruku


def posalji_poruku(msg:str,sign:bool,ziped:bool,encrypt:bool,radix64:bool,
                    private_senderkey_id:str,public_recieverkey_id:str,password:str,algorithm:str,
                    dest_file:str):
    pr_key = None
    pu_key = None
    if sign:
        pr_key = dohvati_objekat_privatni_kljuc(private_senderkey_id, password)
        if pr_key["ERROR"] is True:
            return pr_key
        pr_key = pr_key["info"]
    if encrypt:
        pu_key = dohvati_objekat_javni_kljuc(public_recieverkey_id)
        if pu_key["ERROR"] is True:
            return pu_key
        pu_key = pu_key["info"]




    #----------------------------------Dohvatili kljuceve-----------------------------------------



    if sign:
        potpis, okteti, timestamp = potpisi_poruku(msg,pr_key)

        inner = {
            "signature_timestamp": timestamp,
            "dva_okteta": base64.b64encode(okteti).decode("utf-8"),
            "IDPua": private_senderkey_id,
            "EPra(HASH(timestamp+MSG))": base64.b64encode(potpis).decode("utf-8"),
            "MSG": msg
        }
    else:
        inner = {
            "signature_timestamp": "",
            "dva_okteta": "",
            "IDPua": "",
            "EPra(HASH(timestamp+MSG))": "",
            "MSG":msg
        }

    inner_str = json.dumps(inner)
    inner_bytes = inner_str.encode("utf-8")

    #----------------------------POTPISIVANJE ZAVRSENO----------------------------

    if ziped:
        inner_bytes=zlib.compress(inner_bytes)

    #----------------------------ZIPOVANJE ZAVRSENO----------------------------------


    if encrypt:
        enkriptovan_ks, enkriptovana_poruka, iv = enkriptuj(inner_bytes,pu_key,algorithm)
        middle = {
            "IDEC": algorithm,
            "IDPub": public_recieverkey_id,
            "EPub(Ks)": base64.b64encode(enkriptovan_ks).decode("utf-8"),
            "IV": base64.b64encode(iv).decode("utf-8"),
            "EKs(ZIP(MSG))": base64.b64encode(enkriptovana_poruka).decode("utf-8")

        }
    else:
        if ziped:
            eks_field = base64.b64encode(inner_bytes).decode("utf-8")
        else:
            eks_field = inner
        middle = {
            "IDEC": "",
            "IDPub": "",
            "EPub(Ks)": "",
            "IV": "",
            "EKs(ZIP(MSG))": eks_field
        }

    middle_str = json.dumps(middle)
    middle_bytes = middle_str.encode("utf-8")

    #---------------------------ENKRIPTOVANJE ZAVRSENO----------------------------------------


    if radix64:
        poruka = base64.b64encode(middle_bytes).decode("utf-8")
    else:
        poruka = middle_str

    #------------------------RADIXOVANJE ZAVRSENO----------------------------------

    outer = {
        "signed": sign,
        "zip": ziped,
        "encrypt": encrypt,
        "radix64": radix64,
        "Radix(MSG)": poruka
    }

    with open(dest_file, "w") as f:
        json.dump(outer, f, indent=2) #indent da ne bude sve u 1 redu samo

    return {"ERROR":False, "info":"Uspesno poslata poruka i sacuvana u " + dest_file}


