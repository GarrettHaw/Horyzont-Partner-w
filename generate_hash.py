import hashlib

password = "horyzont2025"
hash_result = hashlib.sha256(password.encode()).hexdigest()
print(f"Password: {password}")
print(f"SHA256 Hash: {hash_result}")
