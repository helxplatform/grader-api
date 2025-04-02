from datetime import datetime, timedelta
from app.models import AssignmentModel

# An uncreated assignment is an assignment with
# either an unset available_date or an unset due_date.
# I.e. available_date is NULL OR due_date is NULL
uncreated_assignment = AssignmentModel(
    name="uncreated",
    directory_path="/uncreated",
    available_date=datetime.now() + timedelta(hours=2),
    due_date=None
)

# A created but not available assignment is an assignment with
# an available date and due date set, but available_date is in the future.
# I.e. available_date in FUTURE
created_not_available_assignment = AssignmentModel(
    name="created_not_available",
    directory_path="/created_not_available",
    available_date=datetime.now() + timedelta(hours=2),
    due_date=datetime.now() + timedelta(hours=4)
)

# An available assignment is a created assignment
# where the available_date is in the past.
# I.e. available_date in PAST
# NOTE: An available assignment can also be closed, and being closed takes precedence.
available_assignment = AssignmentModel(
    name="available",
    directory_path="/available",
    available_date=datetime.now() + timedelta(hours=-2),
    due_date=datetime.now() + timedelta(hours=2)
)

# A closed assignment is a created assignment
# where the due_date is in the past.
# I.e. due_date in PAST
# NOTE: A closed assignment can also be available, but being closed takes precedence.
closed_assignment = AssignmentModel(
    name="closed",
    directory_path="/closed",
    available_date=datetime.now() + timedelta(hours=-4),
    due_date=datetime.now() + timedelta(hours=-2)
)

data = [
    uncreated_assignment,
    created_not_available_assignment,
    available_assignment,
    closed_assignment
]