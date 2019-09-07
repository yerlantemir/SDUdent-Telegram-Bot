import os
from cryptography.fernet import Fernet

key = os.environ.get("ECRYPTION_KEY")
f = Fernet(key)


def encrypt(message):
    return f.encrypt(message.encode()).decode()


def decrypt(message):
    return f.decrypt(message.encode()).decode()
