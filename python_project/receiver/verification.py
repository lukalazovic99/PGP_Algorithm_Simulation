import base64
import hashlib

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, utils


def verify_signature(msg: str, signature_timestamp: str, dva_okteta: bytes, signature: bytes,
                     sender_public_key_pem: str) -> dict[str, str | bool | None]:
    timestamp_msg = (signature_timestamp + " || " + msg).encode("utf-8")
    msg_digest = hashlib.sha1(timestamp_msg).digest()  # bytes

    if msg_digest[:2] != dva_okteta:
        return {
            "valid": False,
            "reason": "dva_okteta_mismatch",
            "received_dva_okteta": dva_okteta.hex().upper(),
            "computed_dva_okteta": msg_digest[:2].hex().upper()
        }  # mozda treba drugi public key kad stigne ovaj return

    try:
        sender_public_key = serialization.load_pem_public_key(sender_public_key_pem.encode("utf-8"))
        sender_public_key.verify(signature, msg_digest,
                                 padding.PSS(mgf=padding.MGF1(hashes.SHA1()), salt_length=padding.PSS.MAX_LENGTH),
                                 utils.Prehashed(hashes.SHA1()))
        return {"valid": True, "reason": "ok"}
    except InvalidSignature:
        return {"valid": False, "reason": "invalid_signature"}
