from typing import List
from uuid import UUID

import requests

from app.celery_app import celery_app
from app.general.db.session import SessionLocal
from app.models import (
    Permission,
    TreeItem,
    Task,
    User
)


@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    return f"test task return {word}"


@celery_app.task
def sync_asset_users(treeitem_id: UUID) -> str:
    db = SessionLocal()
    try:

        treeitem : TreeItem = db.query(TreeItem).filter(
            TreeItem.id == treeitem_id
        ).first()

        print("treeitem", treeitem)
        
        if treeitem.type == "objective":
            tasks = treeitem.children
        elif treeitem.type == "phase":
            tasks = treeitem.tasks
        else:
            tasks = [treeitem]
        
        print("tasks", tasks)

        task: Task
        for task in tasks:
            print(type(task), task)
            permissions = db.query(Permission).filter(
                Permission.treeitem_id.in_(task.path_ids)
            ).all()
            print("task", task)
            print("permissions", permissions)
            print("assets", task.assets)
            
            user_permissions = {}
            perm: Permission
            for perm in permissions:
                for user_id in list(perm.team.user_ids):
                    if not user_id in user_permissions:
                        user : User = db.query(User).filter(User.id == user_id).first()
                        user_permissions[user_id] = {
                            "email": user.email,
                            "access": perm.access_assets_permission,
                            "create": perm.create_assets_permission,
                            "delete": perm.delete_assets_permission,
                        }
                    else:
                        if not user_permissions[user_id]["access"] and perm.access_assets_permission:
                            user_permissions[user_id]["access"] = True
                        if not user_permissions[user_id]["create"] and perm.create_assets_permission:
                            user_permissions[user_id]["create"] = True
                        if not user_permissions[user_id]["delete"] and perm.delete_assets_permission:
                            user_permissions[user_id]["delete"] = True
                             
            for asset in task.assets:
                URL = asset.internal_link + "/sync_users"
                print(URL, user_permissions)
                # requests.post(URL, user_permissions)

    except Exception as e:
        db.close()
        raise e
