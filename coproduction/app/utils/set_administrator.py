from app.general.db.session import SessionLocal
from app.models import User, CoproductionProcess
from app import crud
import asyncio

email = "j.badiola@deusto.es"


async def main():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise Exception("No user found with that email.")

        for coproductionprocess in db.query(CoproductionProcess).all():
            try:
                await crud.coproductionprocess.add_administrator(db=db, db_obj=coproductionprocess, user=user)
            except:
                pass

    except Exception as e:
        print(str(e))
        db.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
