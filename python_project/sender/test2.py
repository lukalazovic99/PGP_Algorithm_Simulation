"""
test_sender.py — flag-ladder tests for preuzmi_podatke()

Runs the sender pipeline through each flag combination, climbing from
simplest (all flags off) to the full nested case (all flags on).

Each test writes an output file and prints what to look for, so you can
open the file and eyeball whether the structure is right.

ADJUST THE IMPORT PATHS below to match your actual filenames before running.
"""

import json
import os

# --- adjust these to your real module paths ---
from keys.rsa_keys import *
from keys.prstenovi_kljuceva import *
from sender.sastavi_i_posalji import posalji_poruku


# Where test output files get written
OUTPUT_DIR = "test_output"

# The message used in every test
TEST_MSG = "Ovo je tajna poruka za test."

# Password placeholder (unused for now — key protection deferred)
TEST_PASSWORD = "test123"


def setup_keys():
    """
    Make sure at least one key pair exists in the rings.
    Generates a fresh pair, then returns a (sender_id, receiver_id) tuple.
    For a solo test, the same pair plays both sender and receiver.
    """
    generisi_kljuceve("Test Sender", "sender@etf.bg", 2048, TEST_PASSWORD)

    priv = load_prsten_privatnih_kljuceva()
    pub = load_prsten_javnih_kljuceva()

    # use the most recently added key for both roles
    sender_id = priv[-1]["key_id"]
    receiver_id = pub[-1]["key_id"]

    print(f"  sender key_id:   {sender_id}")
    print(f"  receiver key_id: {receiver_id}")
    return sender_id, receiver_id


def run_test(name, sign, ziped, encrypt, radix64,
             sender_id, receiver_id, algorithm="AES"):
    """Runs one flag combination and reports where the file landed."""
    print(f"\n=== {name} ===")
    print(f"  sign={sign}  zip={ziped}  encrypt={encrypt}  radix64={radix64}"
          + (f"  algo={algorithm}" if encrypt else ""))

    out_path = os.path.join(OUTPUT_DIR, name + ".json")

    posalji_poruku(
        msg=TEST_MSG,
        sign=sign,
        ziped=ziped,
        encrypt=encrypt,
        radix64=radix64,
        private_senderkey_id=sender_id,
        public_recieverkey_id=receiver_id,
        password=TEST_PASSWORD,
        algorithm=algorithm,
        dest_file=out_path,
    )

    # read it back and show the top-level shape
    with open(out_path, "r") as f:
        data = json.load(f)

    print(f"  -> wrote {out_path}")
    print(f"     flags in file: signed={data['signed']} zip={data['zip']} "
          f"encrypt={data['encrypt']} radix64={data['radix64']}")

    # for the fully-readable case, confirm the message survived
    if not encrypt and not radix64:
        middle = json.loads(data["Radix(MSG)"])
        inner_blob = middle["EKs(ZIP(MSG))"]
        # when not zipped and not encrypted, the blob is base64 of the inner JSON
        if not ziped:
            import base64
            inner = json.loads(base64.b64decode(inner_blob).decode("utf-8"))
            print(f"     recovered MSG: {inner['MSG']!r}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Setting up keys...")
    sender_id, receiver_id = setup_keys()

    # --- the ladder: each test adds one layer of complexity ---
    run_test("test1_plain",        False, False, False, False, sender_id, receiver_id)
    run_test("test2_zip",          False, True,  False, False, sender_id, receiver_id)
    run_test("test3_sign",         True,  False, False, False, sender_id, receiver_id)
    run_test("test4_encrypt_aes",  False, False, True,  False, sender_id, receiver_id, "AES")
    run_test("test5_encrypt_3des", False, False, True,  False, sender_id, receiver_id, "3xDES")
    run_test("test6_full",         True,  True,  True,  True,  sender_id, receiver_id, "AES")

    print("\nAll tests ran. Open the files in", OUTPUT_DIR, "to inspect them.")


if __name__ == "__main__":
    main()