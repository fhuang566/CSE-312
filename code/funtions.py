import hashlib



#authenticate auth_token, if token is valid return username else return false
def authenticate(token, collection):
    if token:
        hashed = hashlib.sha256(token.encode())
        user = collection.find_one({"auth_token": hashed.digest()})
        if user:
            return user["username"]
    return False