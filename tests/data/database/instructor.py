from app.core.role_permissions import admin_role, instructor_role
from app.models import InstructorModel

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