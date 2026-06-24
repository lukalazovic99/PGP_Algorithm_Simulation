import base64


def radixuj(poruka):
    return base64.b64encode(poruka)