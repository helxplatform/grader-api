from app.models import InstructorModel
from app.core.role_permissions import instructor_role, admin_role

basic_instructor = InstructorModel(
    onyen="basicinstructor",
    first_name="Basic",
    last_name="Instructor",
    email="basicinstructor@unc.edu",
    role=instructor_role
)

admin = InstructorModel(
    onyen="admin",
    first_name="Admin",
    last_name="",
    email="admin@renci.org",
    role=admin_role
)

data = [
    basic_instructor,
    admin
]