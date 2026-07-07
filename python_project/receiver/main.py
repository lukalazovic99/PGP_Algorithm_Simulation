import json
import base64
import zlib

from keys.prstenovi_kljuceva import dohvati_javni_kljuc, dohvati_objekat_privatni_kljuc, dohvati_objekat_javni_kljuc
from receiver.decryption import decrypt_session_key
from receiver.decryption import decrypt_payload
from receiver.verification import verify_signature


def unzip(message):
    return zlib.decompress(message)


def decode_base64(message: str) -> bytes:
    return base64.b64decode(message)


def receive_message(outer_message: str,
                    private_key_password: str | None = None) -> dict:
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
        encryption_layer = json.loads(layer1)

    if encrypted:
        receiver_key_id = encryption_layer["IDPub"]
        receiver_private_key = dohvati_objekat_privatni_kljuc(receiver_key_id, private_key_password)
        if receiver_private_key["ERROR"] is True:
            return {"message": None, "result": receiver_private_key["info"]}
        receiver_private_key = receiver_private_key["info"]
        print(
            "Receiver private key object: ",
            receiver_private_key
        )

        session_key = decrypt_session_key(encryption_layer["EPub(Ks)"], receiver_private_key)
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
            payload_bytes = unzip(payload_bytes)
            signed_layer = json.loads(payload_bytes.decode("utf-8"))
        else:
            signed_layer = payload_field

    sig_rs = None
    if signed:
        print("Signed layer: ", signed_layer)
        public_key_id = signed_layer["IDPua"]
        sender_public_key = dohvati_objekat_javni_kljuc(public_key_id)
        if sender_public_key["ERROR"] is True:
            sig_rs = {"valid": False, "reason": sender_public_key["info"]}
        else:
            sender_public_key = sender_public_key["info"]
            sig_rs = verify_signature(signed_layer["MSG"], signed_layer["signature_timestamp"],
                                      decode_base64(signed_layer["dva_okteta"]),
                                      decode_base64(signed_layer["EPra(HASH(timestamp+MSG))"]),
                                      sender_public_key)
        print("Signature verification result: ", sig_rs)
    else:
        sig_rs = {"valid": None, "reason": "not_signed"}

    return {"message": signed_layer["MSG"], "signature_verification_result": sig_rs}
