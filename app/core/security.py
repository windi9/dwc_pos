# dwc_pos/app/core/security.py

from datetime import datetime, timedelta, timezone
from typing import Optional
import secrets # Untuk token verifikasi acak
import string # Untuk PIN acak

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# --- Password Hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# --- PIN Hashing (Opsional: Jika PIN juga ingin di-hash) ---
# Jika PIN hanya 6 digit, hashing mungkin tidak sekuat password,
# tapi tetap lebih baik daripada menyimpan plaintext.
# Untuk demo ini, kita akan menyimpannya plaintext agar mudah,
# tetapi dalam produksi, pertimbangkan untuk hashing PIN juga.
def verify_pin(plain_pin: str, hashed_pin: str) -> bool:
    # Untuk demo, kita asumsikan PIN disimpan hashed jika diaktifkan.
    # Jika tidak dihash, cukup 'return plain_pin == stored_pin'
    return pwd_context.verify(plain_pin, hashed_pin)

def get_pin_hash(pin: str) -> str:
    return pwd_context.hash(pin)

# --- JWT (JSON Web Token) ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # For Web Admin, token might have a very long expiration or no explicit expiration for session persistence
        # For API tokens (e.g., POS App), use ACCESS_TOKEN_EXPIRE_MINUTES
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, str(settings.SECRET_KEY), algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    try:
        decoded_payload = jwt.decode(token, str(settings.SECRET_KEY), algorithms=[settings.ALGORITHM])
        return decoded_payload
    except JWTError:
        return None

# --- Email Verification & PIN Generation ---
# Untuk token aktivasi akun (link)
def generate_verification_token() -> str:
    return secrets.token_urlsafe(32) # Menggunakan URL-safe string untuk link aktivasi

# Untuk kode verifikasi login (6 digit angka)
def generate_verification_code() -> str:
    # Hasilkan 6 digit angka acak
    return ''.join(secrets.choice(string.digits) for _ in range(6))

# Untuk PIN (6 digit angka)
def generate_pin() -> str:
    # Hasilkan 6 digit angka acak
    return ''.join(secrets.choice(string.digits) for _ in range(6))