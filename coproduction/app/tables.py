from sqlalchemy import ARRAY, Column, ForeignKey, String, Table, func

from app.general.db.base_class import Base as BaseModel

team_administrators_association_table = Table('team_administrators', BaseModel.metadata,
                                    Column('team_id', ForeignKey('team.id', ondelete="CASCADE"), primary_key=True),
                                    Column('user_id', ForeignKey('user.id', ondelete="CASCADE"), primary_key=True))


coproductionprocess_administrators_association_table = Table('coproductionprocess_administrators', BaseModel.metadata,
                                    Column('coproductionprocess_id', ForeignKey('coproductionprocess.id', ondelete="CASCADE"), primary_key=True),
                                    Column('user_id', ForeignKey('user.id', ondelete="CASCADE"), primary_key=True))

organization_administrators_association_table = Table('organization_administrators', BaseModel.metadata,
                                    Column('organization_id', ForeignKey('organization.id', ondelete="CASCADE"), primary_key=True),
                                    Column('user_id', ForeignKey('user.id', ondelete="CASCADE"), primary_key=True))

user_team_association_table = Table('association_user_team', BaseModel.metadata,
                                    Column('user_id', ForeignKey('user.id', ondelete="CASCADE"), primary_key=True),
                                    Column('team_id', ForeignKey('team.id', ondelete="CASCADE"), primary_key=True))