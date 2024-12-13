from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, PublicFormat, NoEncryption

def generate_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    public_key_pem = public_key.public_bytes(encoding=Encoding.PEM, format=PublicFormat.SubjectPublicKeyInfo)
    private_key_pem = private_key.private_bytes(encoding=Encoding.PEM, format=PrivateFormat.PKCS8, encryption_algorithm=NoEncryption())
    return private_key_pem, public_key_pem
