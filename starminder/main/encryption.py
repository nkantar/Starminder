from cryptography.fernet import Fernet

from django.conf import settings


fernet = Fernet(settings.ENCRYPTION_KEY)


def encrypt(data: bytes) -> bytes:
    return fernet.encrypt(data)


def decrypt(data: bytes) -> bytes:
    return fernet.decrypt(data)
