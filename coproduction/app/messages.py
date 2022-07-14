import json
import json
from uuid import UUID
import requests
from starlette_context import context
from contextvars import ContextVar

_disable_logging: ContextVar[str] = ContextVar("disable_logging", default=False)

def set_logging_disabled(val: bool) -> str:
    try:
        _disable_logging.set(val)
    except:
        pass

def is_logging_disabled() -> str:
    return  _disable_logging.get()


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)
        
async def log(data: dict):
    if is_logging_disabled():
        print("logging disabled")
        return

    if not "user_id" in data:
        data["user_id"] = context.data.get("user", {}).get("sub", "anonymous")
            
    data["service"] = "coproduction"
    res = requests.post("http://logging/api/v1/log", data=json.dumps(data,cls=UUIDEncoder), timeout=2)
    # print("message sent", res.json())
