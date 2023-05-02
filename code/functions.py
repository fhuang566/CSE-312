import hashlib



#authenticate auth_token, if token is valid return username else return false
def authenticate(token, collection):
    if token:
        hashed = hashlib.sha256(token.encode())
        user = collection.find_one({"auth_token": hashed.digest()})
        if user:
            return user["username"]
    return False

def xsrf_auth(token, collection):
    if token:
        user = collection.find_one({"xsrf_token": token})
        if user:
            return user["username"]
    return False