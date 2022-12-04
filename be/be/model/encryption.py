import hashlib

def encryption(password):
    pw = "20020610" + password + "fyyTQY cty"
    hash = hashlib.sha256()
    hash.update(pw.encode('utf-8'))
    return hash.hexdigest()