import zlib


def zipuj(poruka):
    return zlib.compress(poruka)