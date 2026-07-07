import json
import zlib
import base64

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from sender.potpis import potpisi_poruku
from sender.enkripcija import enkriptuj
from receiver.main import receive_message


def private_pem(key):
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")


def public_pem(key):
    return key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")


sender_private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
receiver_private = rsa.generate_private_key(public_exponent=65537, key_size=2048)

sender_public = sender_private.public_key()
receiver_public = receiver_private.public_key()

sender_public_key_pem = public_pem(sender_public)
receiver_private_key_pem = private_pem(receiver_private)

msg = "hello world"
msg_corrupted = "hello world!"
signature, dva_okteta, timestamp = potpisi_poruku(msg, sender_private)
bad_signature = bytearray(signature)
bad_signature[10] ^= 0x01   # flip one bit
bad_signature = bytes(bad_signature)

signed_layer = {
    "signature_timestamp": timestamp,
    "dva_okteta": base64.b64encode(dva_okteta).decode("ascii"),
    "IDPua": "TEST_SENDER_ID",
    "EPra(HASH(timestamp+MSG))": base64.b64encode(bad_signature).decode("ascii"),
    "MSG": msg
}

signed_layer_bytes = json.dumps(signed_layer).encode("utf-8")
zipped_bytes = zlib.compress(signed_layer_bytes)

epub_ks, eks_msg, iv = enkriptuj(zipped_bytes, receiver_public, "AES")

encryption_layer = {
    "IDEC": "AES",
    "IDPub": "TEST_RECEIVER_ID",
    "EPub(Ks)": base64.b64encode(epub_ks).decode("ascii"),
    "IV": base64.b64encode(iv).decode("ascii"),
    "EKs(ZIP(MSG))": base64.b64encode(eks_msg).decode("ascii")
}

encryption_layer_bytes = json.dumps(encryption_layer).encode("utf-8")

outer_message = {
    "signed": True,
    "zip": True,
    "encrypt": True,
    "radix64": True,
    "Radix(MSG)": base64.b64encode(encryption_layer_bytes).decode("ascii")
}

outer_message_json = json.dumps(outer_message)

result = receive_message(
    outer_message_json,
    receiver_private_key_pem,
    sender_public_key_pem
)

print(json.dumps(result, indent=2))