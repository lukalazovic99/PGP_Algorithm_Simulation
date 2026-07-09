
import json
import os

from keys.rsa_keys import *
from keys.prstenovi_kljuceva import *
from sender.sastavi_i_posalji import *


OUTPUT_DIR = "test_output"
TEST_MSG = "Ovo je tajna poruka za test."



def setup_keys():
    generisi_kljuceve("kljucTestiranja2", "postman@etf.bg", 2048, "test")

    priv = load_prsten_privatnih_kljuceva()
    pub = load_prsten_javnih_kljuceva()

    sender_id = priv[-1]["key_id"]
    receiver_id = pub[-1]["key_id"]

    print(f"  sender key_id:   {sender_id}")
    print(f"  receiver key_id: {receiver_id}")
    return sender_id, receiver_id


def run_test(name, sign, ziped, encrypt, radix64,
             sender_id, receiver_id, algorithm="AES"):

    out_path = os.path.join("test_output", name + ".pgp")

    posalji_poruku(
        msg=TEST_MSG,
        sign=sign,
        ziped=ziped,
        encrypt=encrypt,
        radix64=radix64,
        private_senderkey_id=sender_id,
        public_recieverkey_id=receiver_id,
        password="test",
        algorithm=algorithm,
        dest_file=out_path,
    )




def main():

 #   sender_id, receiver_id = setup_keys()

    priv = load_prsten_privatnih_kljuceva()
    pub = load_prsten_javnih_kljuceva()

    sender_id = priv[-1]["key_id"]
    receiver_id = pub[-1]["key_id"]

    run_test("test1_bez_icega",        False, False, False, False, sender_id, receiver_id)
    run_test("test2_zip",          False, True,  False, False, sender_id, receiver_id)
    run_test("test3_potpisan",         True,  False, False, False, sender_id, receiver_id)
    run_test("test4_encrypt_aes",  False, False, True,  False, sender_id, receiver_id, "AES")
    run_test("test5_encrypt_3des", False, False, True,  False, sender_id, receiver_id, "3xDES")
    run_test("test6_sve",         True,  True,  True,  True,  sender_id, receiver_id, "AES")


if __name__ == "__main__":
    main()