import base64
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from dotenv import load_dotenv

load_dotenv()

# Funzioni di cifratura e decifratura AES
def get_aes_key():
    key_b64 = os.getenv("AES_KEY")
    if not key_b64:
        raise ValueError("❌ AES_KEY non trovata nel .env")
    key = base64.b64decode(key_b64)
    if len(key) != 32:
        raise ValueError("❌ AES_KEY non è lunga 32 byte!")
    return key

# Funzioni di cifratura e decifratura AES
def aes_ecb_encrypt(plaintext: str) -> str:
    """Cifra con AES-ECB (stesso input → stesso output)."""
    key = get_aes_key()
    
    # Padding PKCS7 per allineare a 16 byte
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext.encode()) + padder.finalize()
    
    # Cifratura ECB
    cipher = Cipher(algorithms.AES(key), modes.ECB())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    
    return base64.b64encode(ciphertext).decode()

def aes_ecb_decrypt(encoded: str) -> str:
    """Decifra con AES-ECB."""
    key = get_aes_key()
    ciphertext = base64.b64decode(encoded)
    
    # Decifratura ECB
    cipher = Cipher(algorithms.AES(key), modes.ECB())
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()
    
    # Rimozione padding PKCS7
    unpadder = padding.PKCS7(128).unpadder()
    decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()
    
    return decrypted.decode()

# Funzioni di cifratura e decifratura AES-GCM
def aes_gcm_encrypt(plaintext: str) -> str:
    key = get_aes_key()
    nonce = os.urandom(12)
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
    return base64.b64encode(nonce + encryptor.tag + ciphertext).decode()

def aes_gcm_decrypt(encoded: str) -> str:
    key = get_aes_key()
    data = base64.b64decode(encoded)
    nonce = data[:12]
    tag = data[12:28]
    ciphertext = data[28:]
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag))
    decryptor = cipher.decryptor()
    return (decryptor.update(ciphertext) + decryptor.finalize()).decode()

def aes_gcm_encrypt_bytes(data: bytes) -> str:
    key = get_aes_key()
    nonce = os.urandom(12)
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()
    return base64.b64encode(nonce + encryptor.tag + ciphertext).decode()