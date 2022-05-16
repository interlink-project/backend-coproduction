import json
import os
from base64 import b64encode
import aiormq
import json
from uuid import UUID
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
        
exchange_name = os.environ.get("EXCHANGE_NAME")
rabbitmq_host = os.environ.get("RABBITMQ_HOST")
rabbitmq_user = os.environ.get("RABBITMQ_USER")
rabbitmq_password = os.environ.get("RABBITMQ_PASSWORD")

async def log(data: dict):
    if is_logging_disabled():
        return

    try:
        data["user_id"] = context.data.get("user", {}).get("sub", None)
    except:
        data["user_id"] = None
    data["service"] = "coproduction"

    request = b64encode(json.dumps(data,cls=UUIDEncoder).encode())
    
    connection = await aiormq.connect("amqp://{}:{}@{}/".format(rabbitmq_user, rabbitmq_password, rabbitmq_host))
    channel = await connection.channel()

    await channel.exchange_declare(
        exchange=exchange_name, exchange_type='direct'
    )

    await channel.basic_publish(
        request, 
        routing_key='logging', 
        exchange=exchange_name,
        properties=aiormq.spec.Basic.Properties(
            delivery_mode=2
        )
    )
