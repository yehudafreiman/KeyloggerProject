from cryptography.fernet import Fernet
import os

def encrypt_file(input_filename, output_filename, key):
    f = Fernet(key)
    with open(input_filename, 'rb') as file:
        data = file.read()
    enc = f.encrypt(data)
    with open(output_filename, 'wb') as file:
        file.write(enc)

def decrypt_file(input_filename, output_filename, key):
    f = Fernet(key)
    with open(input_filename, 'rb') as file:
        data = file.read()
    dec = f.decrypt(data)
    with open(output_filename, 'wb') as file:
        file.write(dec)

# מפתח
if not os.path.exists("key.key"):
    key = Fernet.generate_key()
    with open("key.key", "wb") as f:
        f.write(key)
else:
    with open("key.key", "rb") as f:
        key = f.read()

print("Key:", key.decode())

# קבצים
original = 'keyfile.txt'
encrypted = 'keyfile.encrypted'
decrypted = 'keyfile_decrypted.txt'

# הצפנה ופענוח
encrypt_file(original, encrypted, key)
decrypt_file(encrypted, decrypted, key)
print("Encryption & Decryption done.")