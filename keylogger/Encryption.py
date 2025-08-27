# pip install cryptography
from cryptography.fernet import Fernet

# הצפנה
def encrypt_file(input_filename, output_filename, key):
    f = Fernet(key)
    data = open(input_filename, 'rb').read()
    enc = f.encrypt(data)
    open(output_filename, 'wb').write(enc)

# פענוח
def decrypt_file(input_filename, output_filename, key):
    f = Fernet(key)
    data = open(input_filename, 'rb').read()
    dec = f.decrypt(data)
    open(output_filename, 'wb').write(dec)

# מפתח
key = Fernet.generate_key()
with open("key.key", "wb") as f:
    f.write(key)
with open("key.key", "rb") as f:
    key = f.read()
print(key.decode())

# קבצים
original = 'my_text_file.txt'
encrypted = 'my_text_file.encrypted'
decrypted = 'my_text_file_decrypted.txt'

# קובץ לדוגמה
open(original, 'w', encoding='utf-8').write("זהו טקסט סודי שיוצפן.\nשורה נוספת להצפנה.")

# הצפנה ופענוח
encrypt_file(original, encrypted, key)
decrypt_file(encrypted, decrypted, key)