import json
import os
from base64 import b64decode, b64encode
import aiormq
import json
from uuid import UUID
from app.middleware import get_user_id


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)
        
class RabbitBody:
    service: str
    data: dict
    
    def __init__(self, service, data):
        self.service = service
        self.data = data

    def encode(self):
        dicc = {"service": self.service, "data": self.data}
        return b64encode(json.dumps(dicc,cls=UUIDEncoder).encode())

    @staticmethod
    def decode(encoded):
        dicc = json.loads(b64decode(encoded))
        return RabbitBody(**dicc)
        
exchange_name = os.environ.get("EXCHANGE_NAME")
rabbitmq_host = os.environ.get("RABBITMQ_HOST")
rabbitmq_user = os.environ.get("RABBITMQ_USER")
rabbitmq_password = os.environ.get("RABBITMQ_PASSWORD")

async def log(data: dict):
    data["user_id"] = get_user_id()
    request = RabbitBody("coproduction", data)
    
    connection = await aiormq.connect("amqp://{}:{}@{}/".format(rabbitmq_user, rabbitmq_password, rabbitmq_host))
    channel = await connection.channel()

    await channel.exchange_declare(
        exchange=exchange_name, exchange_type='direct'
    )

    await channel.basic_publish(
        request.encode(), 
        routing_key='logging', 
        exchange=exchange_name,
        properties=aiormq.spec.Basic.Properties(
            delivery_mode=2
        )
    )
    print("MENSAJE ENVIADO POR RABBITMQ")
