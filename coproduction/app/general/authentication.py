from base64 import b64decode
import jwt
import logging

import requests
from app.config import settings
from cryptography.hazmat.primitives import serialization

logging.basicConfig(level=logging.DEBUG)

url = "http://auth1.localhost/auth/realms/greengage"

def decode_token(jwtoken):
    keycloak_realm = requests.get(url)
    keycloak_realm.raise_for_status()
    key_der_base64 = keycloak_realm.json()["public_key"]
    key_der = b64decode(key_der_base64.encode())

    public_key = serialization.load_der_public_key(key_der)

    payload = jwt.decode(jwtoken, public_key, algorithms=["RS256"], 
                         audience=settings.KEYCLOAK_CLIENT_ID)
    return payload