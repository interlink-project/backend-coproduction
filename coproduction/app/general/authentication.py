import jwt
import requests
from base64 import b64decode
from app.config import settings
from cryptography.hazmat.primitives import serialization

url = settings.KEYCLOAK_URL_REALM

def decode_token(jwtoken):
    keycloak_realm = requests.get(url)
    keycloak_realm.raise_for_status()
    key_der_base64 = keycloak_realm.json()["public_key"]
    key_der = b64decode(key_der_base64.encode())
    public_key = serialization.load_der_public_key(key_der)
    payload = jwt.decode(jwtoken, public_key, algorithms=["RS256"], 
                         audience=settings.KEYCLOAK_CLIENT_ID)
    return payload