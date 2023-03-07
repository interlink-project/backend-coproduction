import jwt
import os
from jwt import PyJWKClient

url = os.getenv("AUTH0_JWK_URL", "")


def decode_token(jwtoken):
    jwks_client = PyJWKClient(url)
    signing_key = jwks_client.get_signing_key_from_jwt(jwtoken)
    data = jwt.decode(
        jwtoken,
        signing_key.key,
        algorithms=["RS256"],
        audience=os.getenv("AUTH0_CLIENT_ID", ""),
        # options={"verify_nbf": False},
    )
    return data
