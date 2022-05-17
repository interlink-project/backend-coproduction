from sqlalchemy import ARRAY, Column, ForeignKey, String, Table, func

from app.general.db.base_class import Base as BaseModel

user_team_association_table = Table('association_user_team', BaseModel.metadata,
                                    Column('user_id', ForeignKey('user.id', ondelete="CASCADE"), primary_key=True),
                                    Column('team_id', ForeignKey('team.id', ondelete="CASCADE"), primary_key=True))

team_role_association_table = Table('association_team_role', BaseModel.metadata,
                                    Column('team_id', ForeignKey('team.id', ondelete="CASCADE"), primary_key=True),
                                    Column('role_id', ForeignKey('role.id', ondelete="CASCADE"), primary_key=True))

user_association_table = Table('association_user_role', BaseModel.metadata,
                               Column('user_id', ForeignKey('user.id', ondelete="CASCADE"), primary_key=True),
                               Column('role_id', ForeignKey('role.id', ondelete="CASCADE"), primary_key=True))
