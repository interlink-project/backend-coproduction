import requests
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_acl(data={
    "scope": {
        "create": [],
        "delete": [],
        "retrieve": [
            "editor",
            "commenter",
            "reader"
        ],
        "update": [
            "editor"
        ],
        "comment": [
            "editor",
            "commenter"
        ]
    }
}):
    logger.debug(f"Call to an external service: http://{settings.ACL_SERVICE}/api/v1/resources/")
    response = requests.post(f"http://{settings.ACL_SERVICE}/api/v1/resources/",
                             json=data)
    return response.json()


def get_permissions_for_role(acl_id: str, role: str):
    logger.debug(f"Call to an external service: http://{settings.ACL_SERVICE}/api/v1/resources/")
    response = requests.get(f"http://{settings.ACL_SERVICE}/api/v1/resources/{acl_id}/permissions/{role}/")
    return response.json()

def check_permissions_for_action(acl_id: str, action: str, role: str):
    logger.debug(f"Call to an external service: http://{settings.ACL_SERVICE}/api/v1/resources/{acl_id}/check/{role}:{action}/")
    response = requests.get(f"http://{settings.ACL_SERVICE}/api/v1/resources/{acl_id}/check/{role}:{action}/")
    return response.json() == True