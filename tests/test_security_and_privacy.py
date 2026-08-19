import pytest
from app.core.security import (
    hash_password, verify_password,
    create_access_token, decode_access_token,
    encrypt_phi, decrypt_phi, hash_ip
)

def test_password_hashing():
    pw = "SecretMedPass123!"
    hashed = hash_password(pw)
    assert hashed != pw
    assert verify_password(pw, hashed) is True
    assert verify_password("WrongPass", hashed) is False

def test_jwt_token_roundtrip():
    data = {"sub": "42", "email": "test@clinic.org"}
    token = create_access_token(data)
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "42"
    assert decoded["email"] == "test@clinic.org"

def test_phi_column_encryption():
    phi_text = "Patient diagnosed with Type 2 Diabetes; takes Metformin 500mg daily. Allergic to Penicillin."
    encrypted = encrypt_phi(phi_text)
    assert encrypted != phi_text
    assert "Diabetes" not in encrypted
    
    decrypted = decrypt_phi(encrypted)
    assert decrypted == phi_text

def test_ip_anonymized_hashing():
    ip = "192.168.1.105"
    h1 = hash_ip(ip)
    h2 = hash_ip(ip)
    assert h1 == h2
    assert ip not in h1
    assert len(h1) == 32
