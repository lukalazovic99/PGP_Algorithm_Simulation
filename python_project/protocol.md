# PGP Simulation Protocol

This document describes the current message structure used between sender and receiver.

It follows the shorthand in `Tekstualne_stvari/format_poruke.txt`, but makes the packet layout explicit as JSON.

## General Rules

1. The outer packet always contains the same top-level flags:
   - `signed`
   - `zip`
   - `encrypt`
   - `radix64`
2. Binary data is not stored directly in JSON.
3. Any encrypted, hashed, signed, or IV byte sequence stored in JSON must be Base64 text.
4. When a flag is `false`, the field layout still exists, but the next inner layer may appear directly as a nested JSON object instead of Base64 text.
5. Size annotations like `-64b`, `-1024b`, `-16b` are comments about expected size. They are not part of the JSON field names.

## Service Order

Logical order of wrapping:

1. Sign message
2. ZIP message
3. Encrypt zipped payload with session key
4. Optionally Radix-64 encode the encryption layer

The receiver unwraps the message in reverse order.

## Outer Packet

The outer packet always has this shape:

```json
{
  "signed": true,
  "zip": true,
  "encrypt": true,
  "radix64": true,
  "Radix(MSG)": "..."
}
```

Field meaning:

- `signed`: whether the signature layer is active
- `zip`: whether ZIP compression is active
- `encrypt`: whether symmetric encryption is active
- `radix64`: whether the encryption layer is wrapped as Base64 text
- `Radix(MSG)`: the next inner layer

Rules for `Radix(MSG)`:

- If `radix64 == true`, `Radix(MSG)` is a Base64 string containing the serialized encryption-layer bytes.
- If `radix64 == false`, `Radix(MSG)` is the encryption-layer object directly.

## Encryption Layer

The encryption layer has this shape:

```json
{
  "IDEC": "3DES",
  "IDPub": "54D7B5FF707FBF41",
  "EPub(Ks)": "base64...",
  "IV": "base64...",
  "EKs(ZIP(MSG))": "..."
}
```

Field meaning:

- `IDEC`: symmetric algorithm identifier, currently `AES128` or `3DES`
- `IDPub`: recipient key ID
- `EPub(Ks)`: session key encrypted with recipient public RSA key
- `IV`: initialization vector for the symmetric algorithm
- `EKs(ZIP(MSG))`: payload protected with the session key

Rules:

- If `encrypt == true`:
  - `IDEC` is a string, either `AES128` or `3DES`
  - `IDPub` is the recipient key ID
  - `EPub(Ks)` is a Base64 string
  - `IV` is a Base64 string
  - `EKs(ZIP(MSG))` is a Base64 string containing ciphertext bytes

- If `encrypt == false`:
  - `IDEC` is `null`
  - `IDPub` is `null`
  - `EPub(Ks)` is `null`
  - `IV` is `null`
  - `EKs(ZIP(MSG))` contains the next inner layer directly:
    - if `zip == true`, it is a Base64 string of zipped bytes
    - if `zip == false`, it is the signed payload object directly

## Signed Payload Layer

The signed payload layer has this shape:

```json
{
  "signature_timestamp": "2026-07-06 18:42:11",
  "dva_okteta": "base64...",
  "IDPua": "FF7D635E930D5463",
  "EPra(HASH(timestamp+MSG))": "base64...",
  "MSG": "plaintext message"
}
```

Field meaning:

- `signature_timestamp`: timestamp used when the signature is formed
- `dva_okteta`: the first 2 bytes of the message digest
- `IDPua`: sender key ID
- `EPra(HASH(timestamp+MSG))`: RSA signature bytes
- `MSG`: message body

Rules:

- If `signed == true`:
  - `signature_timestamp` is a timestamp string in the format:
    - `%Y-%m-%d %H:%M:%S`
  - `dva_okteta` is a Base64 string for the first 2 digest bytes
  - `IDPua` is sender key ID
  - `EPra(HASH(timestamp+MSG))` is a Base64 string
  - `MSG` is present

- If `signed == false`:
  - `signature_timestamp` is `null`
  - `dva_okteta` is `null`
  - `IDPua` is `null`
  - `EPra(HASH(timestamp+MSG))` is `null`
  - `MSG` is still present

## Message Content

The current shorthand defines:

```json
{
  "MSG": "plaintext message"
}
```

So the current structure treats `MSG` as a string.

Receiver code may later accept a richer object form, but the current protocol shape uses a string `MSG`.

## Signature Input

The current signing input is:

```text
signature_timestamp + " || " + MSG
```

Where:

- `signature_timestamp` is the string stored in the packet
- `MSG` is the plaintext message string

Then:

1. Compute SHA-1 over that byte sequence
2. Store the first 2 digest bytes in `dva_okteta` as Base64 text
3. Sign the SHA-1 digest with the sender private RSA key
4. Store the signature bytes in `EPra(HASH(timestamp+MSG))` as Base64 text

This document does not fix a JSON canonicalization rule yet. That can be added later if the message payload stops being a plain string and becomes a structured object.

## Compression

If `zip == true`:

- ZIP is applied to the signed payload bytes before encryption

If `zip == false`:

- the signed payload remains uncompressed

## Encryption

Current symmetric algorithms:

- `AES128`
- `3DES`

Rules:

1. A session key `Ks` is generated per message.
2. `Ks` is encrypted with the recipient public RSA key and stored in `EPub(Ks)`.
3. The payload bytes are encrypted with `Ks`.
4. The IV is stored in `IV` as Base64 text.

## Key IDs

Key ID is defined as the least significant 64 bits of the RSA public modulus:

```python
key_id = format(public_numbers.n % (2 ** 64), "016X")
```

This applies to:

- `IDPub`: recipient key ID
- `IDPua`: sender key ID

## Full Example: All Flags True

Outer packet:

```json
{
  "signed": true,
  "zip": true,
  "encrypt": true,
  "radix64": true,
  "Radix(MSG)": "base64(serialized encryption-layer bytes)"
}
```

Decoded `Radix(MSG)`:

```json
{
  "IDEC": "AES128",
  "IDPub": "54D7B5FF707FBF41",
  "EPub(Ks)": "base64(rsa_encrypted_session_key)",
  "IV": "base64(iv_bytes)",
  "EKs(ZIP(MSG))": "base64(ciphertext)"
}
```

Decrypted and unzipped payload:

```json
{
  "signature_timestamp": "2026-07-06 18:42:11",
  "dva_okteta": "base64(first_two_digest_bytes)",
  "IDPua": "FF7D635E930D5463",
  "EPra(HASH(timestamp+MSG))": "base64(signature_bytes)",
  "MSG": "plaintext message"
}
```

## Full Example: `radix64 == false`

```json
{
  "signed": true,
  "zip": true,
  "encrypt": true,
  "radix64": false,
  "Radix(MSG)": {
    "IDEC": "3DES",
    "IDPub": "54D7B5FF707FBF41",
    "EPub(Ks)": "base64...",
    "IV": "base64...",
    "EKs(ZIP(MSG))": "base64..."
  }
}
```

## Full Example: `encrypt == false` and `zip == false`

```json
{
  "signed": true,
  "zip": false,
  "encrypt": false,
  "radix64": false,
  "Radix(MSG)": {
    "IDEC": null,
    "IDPub": null,
    "EPub(Ks)": null,
    "IV": null,
    "EKs(ZIP(MSG))": {
      "signature_timestamp": "2026-07-06 18:42:11",
      "dva_okteta": "base64...",
      "IDPua": "FF7D635E930D5463",
      "EPra(HASH(timestamp+MSG))": "base64...",
      "MSG": "plaintext message"
    }
  }
}
```

## Full Example: `signed == false`

```json
{
  "signature_timestamp": null,
  "dva_okteta": null,
  "IDPua": null,
  "EPra(HASH(timestamp+MSG))": null,
  "MSG": "plaintext message"
}
```
