from typing import List
from uuid import UUID
import requests
from sqlalchemy import and_, or_
from app.celery_app import celery_app
from app.general.db.session import SessionLocal
from app.models import (
    Permission,
    TreeItem,
    Task,
    User,
    Team,
    CoproductionProcess,
    InternalAsset,
    user_team_association_table,
    coproductionprocess_administrators_association_table
)
from app import crud


@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    return f"test task return {word}"


def iterate(db, treeitems: List[TreeItem] = [], coproductionprocesses: List[CoproductionProcess] = []):
    # get all the tasks behind the treeitems or the coproductionprocess
    tasks = {}
    for treeitem in treeitems:
        if treeitem.type == "objective":
            for task in treeitem.children:
                tasks[task.id] = task
        elif treeitem.type == "phase":
            for task in treeitem.tasks:
                tasks[task.id] = task
        else:
            tasks[treeitem.id] = treeitem

    for coproductionprocess in coproductionprocesses:
        for phase in coproductionprocess.children:
            for objective in phase.children:
                for task in objective.children:
                    tasks[task.id] = task

    # get users and their permissions for every task and call /sync_users of the software interlinkers used by the assets of the task
    task: Task
    for task_id, task in tasks.items():
        try:
            permissions = db.query(
                Permission
            ).filter(
                and_(
                    Permission.coproductionprocess_id == task.coproductionprocess.id,
                    Permission.treeitem_id.in_(task.path_ids),
                )
            ).distinct().all()

            res = db.query(
                User
            ).join(
                user_team_association_table
            ).filter(
                Team.id.in_([permission.team_id for permission in permissions])
            )

            res2 = db.query(
                User
            ).join(
                coproductionprocess_administrators_association_table
            ).filter(
                CoproductionProcess.id == task.coproductionprocess.id
            )

            users = res.union(res2).distinct().all()

            data = []
            for user in users:
                if crud.permission.get_dict_for_user_and_treeitem(db=db, treeitem=task, user=user).get("access_assets_permission", False):
                    toAdd = {
                        "emails": [user.email] + user.additionalEmails,
                        "user_id": user.id,
                        "administrator": user in task.coproductionprocess.administrators
                    }
                    data.append(toAdd)

            # for asset in task.assets:
            #     if type(asset) == InternalAsset:
            #         URL = asset.internal_link + "/sync_users"
            #         print(URL, data)
            #         try:
            #             requests.post(URL, json=data)
            #         except Exception as e:
            #             print(str(e))
        except Exception as e:
            print("==========================" )
            print(task)
            print(task_id)
            print("The task tiene un problema: task con id")
            print(str(e))


@celery_app.task
def sync_asset_users(user_ids: List[str]) -> str:
    db = SessionLocal()

    # get the teams of the users
    teams = db.query(
        Team.id
    ).join(
        user_team_association_table
    ).filter(
        User.id.in_(user_ids)
    ).distinct().all()

    # get the treeitems where the teams of the users are working on
    treeitems: TreeItem = db.query(
        TreeItem
    ).join(
        Permission
    ).filter(
        or_(
            Permission.team_id.in_([team.id for team in teams])
        )
    ).distinct().all()

    # get the coproductionprocesses where the users are admins
    coproductionprocesses = db.query(
        CoproductionProcess
    ).join(
        coproductionprocess_administrators_association_table
    ).filter(
        User.id.in_(user_ids)
    ).distinct().all()

    try:
        iterate(db, treeitems=treeitems, coproductionprocesses=coproductionprocesses)

    except Exception as e:
        db.close()
        raise e


@celery_app.task
def sync_asset_treeitems(treeitem_ids: List[UUID]) -> str:
    db = SessionLocal()

    treeitems: TreeItem = db.query(TreeItem).filter(
        TreeItem.id.in_(treeitem_ids)
    ).all()

    try:
        iterate(db, treeitems)

    except Exception as e:
        db.close()
        raise e
