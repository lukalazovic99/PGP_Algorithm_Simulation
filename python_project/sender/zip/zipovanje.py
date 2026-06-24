import zlib


def zipuj(poruka):
    poruka = poruka.encode("utf-8") #ovo je jer neke byte prima zli b
    return zlib.compress(poruka)