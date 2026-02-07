from cryptography.fernet import Fernet

key = Fernet.generate_key()
with open("shared_key.txt", "wb") as f:
    f.write(key)

print("Key generated.")
