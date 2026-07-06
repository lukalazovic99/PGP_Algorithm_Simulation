import hashlib
from datetime import datetime

from cryptography.hazmat.primitives.asymmetric import padding, utils
from cryptography.hazmat.primitives import hashes


#   " || " kao podeoka izmedju 1)timestamp_potpisa i 2) data MSG


def hesiraj_poruku(stvar): #prima poruku u bytes o tome se staramo u sastavljanju
    sha1 = hashlib.sha1()
    sha1.update(stvar)
    return sha1.digest() #vraca 20 bytes

def potpisi_poruku(poruka:str,key): #poruka u stringu koja se nalepi na timestamp:str + " || "
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp_msg = (timestamp + " || " + poruka).encode("utf-8")
    h = hesiraj_poruku(timestamp_msg)
    dva_okteta = h[:2]
    potpis = key.sign(
        h,
        padding.PKCS1v15(),
        utils.Prehashed(hashes.SHA1())
    )
    return potpis, dva_okteta, timestamp

