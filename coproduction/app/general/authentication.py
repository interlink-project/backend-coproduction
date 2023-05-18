import jwt
from jwt import PyJWKClient
import os

url = "https://aac.platform.smartcommunitylab.it/jwk"

def decode_token(jwtoken):
    jwks_client = PyJWKClient(url)
    signing_key = jwks_client.get_signing_key_from_jwt(jwtoken)
    data = jwt.decode(
        jwtoken,
        signing_key.key,
        algorithms=["RS256"],
        audience=os.getenv("CLIENT_ID"),
        # options={"verify_nbf": False},
    )
    return data