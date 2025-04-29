from app.models import InstructorModel
from app.core.role_permissions import TestInstructorRole, TestAdminRole

basic_instructor = InstructorModel(
    onyen="basicinstructor",
    first_name="Basic",
    last_name="Instructor",
    email="basicinstructor@unc.edu",
    role=TestInstructorRole()
)

admin = InstructorModel(
    onyen="admin",
    first_name="Admin",
    last_name="",
    email="admin@renci.org",
    role=TestAdminRole()
)

data = [
    basic_instructor,
    admin
]