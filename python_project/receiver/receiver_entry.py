from receiver.main import receive_message

def receive_message_from_file(
        input_path: str,
        private_key_password: str,
) -> dict[str, object]:
    with open(input_path, "r", encoding="utf-8") as f:
        outer_message = f.read()

    return receive_message(
        outer_message,
        private_key_password
    )
