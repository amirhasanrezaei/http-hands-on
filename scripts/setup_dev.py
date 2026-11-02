"""
Create a local RSA key pair, a JWKS file for Envoy, and a short-lived test JWT.

This is only a development/demo issuer. Do not use its private key or tokens
for a production system.
"""

from __future__ import annotations

import base64
import json
import time
from pathlib import Path

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


ROOT = Path(__file__).resolve().parents[1]
KEYS_DIR = ROOT / "keys"
PRIVATE_KEY_FILE = KEYS_DIR / "private_key.pem"
JWKS_FILE = ROOT / "envoy" / "jwks.json"
TOKEN_FILE = ROOT / "token.txt"

ISSUER = "https://http-practice.local"
AUDIENCE = "httpbin-api"
KEY_ID = "local-dev-rsa-key"


def base64url_uint(value: int) -> str:
    """Encode an RSA public-key integer as an unpadded Base64URL string."""
    byte_length = (value.bit_length() + 7) // 8
    raw = value.to_bytes(byte_length, byteorder="big")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def main() -> None:
    KEYS_DIR.mkdir(parents=True, exist_ok=True)
    JWKS_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Create a 2048-bit RSA key pair. Only the public key goes into JWKS.
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    PRIVATE_KEY_FILE.write_bytes(private_pem)

    public_numbers = private_key.public_key().public_numbers()
    jwks = {
        "keys": [
            {
                "kty": "RSA",
                "use": "sig",
                "alg": "RS256",
                "kid": KEY_ID,
                "n": base64url_uint(public_numbers.n),
                "e": base64url_uint(public_numbers.e),
            }
        ]
    }
    JWKS_FILE.write_text(
        json.dumps(jwks, indent=2) + "\n",
        encoding="utf-8",
    )

    now = int(time.time())
    claims = {
        "iss": ISSUER,
        "sub": "local-student",
        "aud": AUDIENCE,
        "iat": now,
        "exp": now + 60 * 60,
    }

    token = jwt.encode(
        claims,
        private_pem,
        algorithm="RS256",
        headers={"kid": KEY_ID},
    )
    TOKEN_FILE.write_text(token, encoding="utf-8")

    print("Development key pair and JWT created.")
    print(f"Public JWKS: {JWKS_FILE.relative_to(ROOT)}")
    print(f"Private key (never commit): {PRIVATE_KEY_FILE.relative_to(ROOT)}")
    print(f"Test token (never commit): {TOKEN_FILE.relative_to(ROOT)}")
    print("The token expires in 60 minutes.")


if __name__ == "__main__":
    main()
