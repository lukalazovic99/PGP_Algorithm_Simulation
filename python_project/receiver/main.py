import json
import r64_zip
def receive_message(outer_message):
    print("MSG: ",outer_message)

    outer_message = json.loads(outer_message)
    print("Outer: ",outer_message)

    message = outer_message["Radix(MSG)"]

    ##if outer_message["radix64"]:
    message = r64_zip.decode_base64(message)
    print("Unradixed: ",message)

    message = json.loads(message)
    print("Inner1: ",message)

    encrypted_session_key = r64_zip.decode_base64(message["EPub(Ks)"])
    print("Encrypted session key: ",encrypted_session_key)

    ciphertext = r64_zip.decode_base64(message["Eks(ZIP(MSG))"])
    print("Ciphertext: ",ciphertext)