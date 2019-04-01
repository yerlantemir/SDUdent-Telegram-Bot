import Crypto.Random
from Crypto.Cipher import AES
import hashlib
from cryptography.fernet import Fernet
import secret_data as sd


key = sd.get_key()
f = Fernet(key)

def encrypt(message):
    return f.encrypt(message.encode()).decode()

def decrypt(message):
    return f.decrypt(message.encode()).decode()

