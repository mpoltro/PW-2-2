import hashlib

# Funzioni di hashing per password
def hash_password(password, salt, pepper):
    """Ritorna un hash SHA-256 con salt + pepper"""
    pwd_bytes = password.encode('utf-8')
    pepper_bytes = pepper.encode('utf-8')
    return hashlib.sha256(salt + pwd_bytes + pepper_bytes).hexdigest()

def hash_otp(otp):
    otp_bytes = otp.encode('utf-8')
    return hashlib.sha256(otp_bytes).hexdigest()

# Controllo OTP
def check_otp_hash(otp: str, hashed_otp: str) -> bool:
    """Verifica se un OTP corrisponde all'hash salvato"""
    return hash_otp(otp) == hashed_otp
