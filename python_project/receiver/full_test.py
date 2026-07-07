from sender.sastavi_i_posalji import posalji_poruku
from receiver.receiver_entry import receive_message_from_file

input_path = "test_mailbox/real_keys_test.pgp"

posalji_poruku(
    msg="hello from real keys",
    sign=True,
    ziped=True,
    encrypt=True,
    radix64=True,
    private_senderkey_id="0C014ED79C9B49ED",
    public_recieverkey_id="CC4A980E8616BB8D",
    password="ipMANcar1234",
    algorithm="AES",
    dest_file=input_path,
)

result = receive_message_from_file(
    input_path,
    private_key_password="wtf",
)
print(result)