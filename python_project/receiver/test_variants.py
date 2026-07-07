from pathlib import Path

from receiver.receiver_entry import receive_message_from_file
from sender.sastavi_i_posalji import posalji_poruku


# Existing real keys from the current key rings
SENDER_ID = "0C014ED79C9B49ED"      # Bogdan
SENDER_PASSWORD = "ipMANcar1234"

RECEIVER_ID = "CC4A980E8616BB8D"    # Luka Skoko
RECEIVER_PASSWORD = "wtf"

TEST_MSG = "Ovo je tajna poruka za test."
OUTPUT_DIR = Path(__file__).resolve().parent / "test_mailbox" / "variants"


def run_case(
    name: str,
    sign: bool,
    ziped: bool,
    encrypt: bool,
    radix64: bool,
    algorithm: str = "AES",
) -> None:
    out_path = OUTPUT_DIR / f"{name}.json"

    print(f"\n=== {name} ===")
    print(
        f"sign={sign} zip={ziped} encrypt={encrypt} radix64={radix64}"
        + (f" algorithm={algorithm}" if encrypt else "")
    )

    posalji_poruku(
        msg=TEST_MSG,
        sign=sign,
        ziped=ziped,
        encrypt=encrypt,
        radix64=radix64,
        private_senderkey_id=SENDER_ID,
        public_recieverkey_id=RECEIVER_ID,
        password=SENDER_PASSWORD,
        algorithm=algorithm,
        dest_file=str(out_path),
    )

    result = receive_message_from_file(
        str(out_path),
        RECEIVER_PASSWORD,
    )

    print("result:", result)

    if result["message"] != TEST_MSG:
        print("  !! MESSAGE MISMATCH !!")

    sig_rs = result["signature_verification_result"]
    if sign:
        if sig_rs["valid"] is not True:
            print("  !! SIGNATURE SHOULD HAVE BEEN VALID !!")
    else:
        if sig_rs["reason"] != "not_signed":
            print("  !! UNSIGNED CASE NOT REPORTED CORRECTLY !!")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    run_case("plain", False, False, False, False)
    run_case("zip_only", False, True, False, False)
    run_case("sign_only", True, False, False, False)
    run_case("encrypt_aes_only", False, False, True, False, "AES")
    run_case("encrypt_3des_only", False, False, True, False, "3xDES")
    run_case("sign_zip", True, True, False, False)
    run_case("encrypt_zip_aes", False, True, True, False, "AES")
    run_case("full_aes", True, True, True, True, "AES")


if __name__ == "__main__":
    main()
