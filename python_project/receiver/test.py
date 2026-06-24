import json
import base64

from receiver.main import receive_message


encrypted_session_key = b"fake encrypted session key"
ciphertext = b"fake ciphertext"

inner_message = {
    "EPub(Ks)": base64.b64encode(encrypted_session_key).decode("ascii"),
    "Eks(ZIP(MSG))": base64.b64encode(ciphertext).decode("ascii")
}

inner_message_json = json.dumps(inner_message).encode("utf-8")

outer_message = {
    "signed": True,
    "zip": True,
    "encrypt": True,
    "radix64": True,
    "Radix(MSG)": base64.b64encode(inner_message_json).decode("ascii")
}

outer_message_json = json.dumps(outer_message)

receive_message(outer_message_json)