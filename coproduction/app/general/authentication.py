
import json

import jwt
import requests
from app.config import settings
from authlib.integrations.starlette_client import OAuth
from jwt import PyJWKClient
from starlette.middleware.base import BaseHTTPMiddleware

url = "https://aac.platform.smartcommunitylab.it/jwk"

oauth = OAuth()
oauth.register(
    name='smartcommunitylab',
    client_id=settings.CLIENT_ID,
    client_secret=settings.CLIENT_SECRET,
    server_metadata_url=settings.SERVER_METADATA_URL,
    client_kwargs={
        'scope': 'openid profile email offline_access'
    }
)


def decode_token(jwtoken):
    jwks_client = PyJWKClient(url)
    signing_key = jwks_client.get_signing_key_from_jwt(jwtoken)
    data = jwt.decode(
        jwtoken,
        signing_key.key,
        algorithms=["RS256"],
        audience="c_0e0822df-9df8-48d6-b4d9-c542a4623f1b",
        # options={"verify_exp": False},
    )
    return data

"""
class AuthMiddleware(BaseHTTPMiddleware):
    
    Middleware that gets token from cookie or authorization headers and loads users data (decoding that token) 
    into request state
    

    def get_token_in_cookie(self, request):
        try:
            return request.cookies.get("auth_token")
        except:
            return None

    def get_token_in_header(self, request):
        try:
            return request.headers.get('authorization').replace("Bearer ", "")
        except:
            return None

    async def dispatch(self, request, call_next):
        token = self.get_token_in_cookie(
            request) or self.get_token_in_header(request)
            
        if not token:
            print("NO TOKEN")
            return await call_next(request)
        try:
            user_data = decode_token(token)
            
            email = user_data["email"]

            # get user by email contained in token after being verified
            response = requests.get(
                f"http://proxy/users/api/v1/users/get_by_email/{email}/")
            user = json.loads(response._content)

            if not user_data:
                raise Exception("Not user data in token")

            if not user:
                # if user does not exist yet, save it on database
                res = requests.post(
                    f"http://proxy/users/api/v1/users/", data=user_data)
                # TODO check res status
                user = json.loads(res._content)
            else:
                # if database user model has outdated info, update
                x = user
                id = x["id"]
                shared_items = {
                    k: x[k] for k in x if k in user_data and x[k] == user_data[k]}
                if not all(k in shared_items for k in ['given_name', 'email', 'locale', 'family_name', 'picture']):
                    print("user needs to be updated")
                    res = requests.patch(f"http://proxy/users/api/v1/users/{id}/", data=user_data)
                    # TODO check res status
                    user = json.loads(res._content)

            print(user)
           
            request.state.user = user_data
            request.state.token = token
            return await call_next(request)

        except Exception as e:
            print(e)
            # TODO: do smthing with the exception
            response = await call_next(request)
            response.delete_cookie(key="auth_token")
            return response
 """