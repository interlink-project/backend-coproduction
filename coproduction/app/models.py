from app.assets.models import *
from app.coproductionprocesses.models import *
from app.coproductionschemas.models import *
from app.phases.models import *
from app.objectives.models import *
from app.tasks.models import *
from app.teams.models import *
from app.users.models import *
from app.roles.models import *

# @event.listens_for(Objective, "after_update")
# def after_objective_update(mapper, connection, instance):