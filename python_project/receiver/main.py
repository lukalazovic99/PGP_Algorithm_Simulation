import json
import base64
import zlib

from receiver.decryption import decrypt_session_key
from receiver.decryption import decrypt_payload


def unzip(message):
    return zlib.decompress(message)


def decode_base64(message):
    return base64.b64decode(message)


def receive_message(outer_message, private_key_pem, sender_public_key_pem, private_key_password=None):
    print("MSG: ", outer_message)

    outer = json.loads(outer_message)

    signed = outer["signed"]
    zipped = outer["zip"]
    encrypted = outer["encrypt"]
    radix64 = outer["radix64"]

    layer1 = outer["Radix(MSG)"]

    if radix64:
        layer1_bytes = decode_base64(layer1)
        encryption_layer = json.loads(layer1_bytes.decode("utf-8"))
    else:
        encryption_layer = layer1

    if encrypted:
        session_key = decrypt_session_key(encryption_layer["EPub(Ks)"], private_key_pem)
        payload_bytes = decrypt_payload(encryption_layer["EKs(ZIP(MSG))"],
                                        session_key,
                                        encryption_layer["IV"],
                                        encryption_layer["IDEC"])
        if zipped:
            signed_layer_bytes = unzip(payload_bytes)
            signed_layer = json.loads(signed_layer_bytes.decode("utf-8"))
        else:
            signed_layer = json.loads(payload_bytes.decode("utf-8"))
    else:
        payload_field = encryption_layer["EKs(ZIP(MSG))"]
        if zipped:
            payload_bytes = decode_base64(payload_field)
            signed_layer_bytes = unzip(payload_bytes)
            signed_layer = json.loads(signed_layer_bytes.decode("utf-8"))
        else:
            signed_layer = payload_field
