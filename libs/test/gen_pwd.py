import hashlib

pwd="100969"
hash_object = hashlib.sha256()
hash_object.update(pwd.encode())
hash_password = hash_object.hexdigest()

print(hash_password)