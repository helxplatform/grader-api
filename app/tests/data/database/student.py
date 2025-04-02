from datetime import datetime, timedelta
from app.models import StudentModel
from app.core.role_permissions import student_role

basic_student = StudentModel(
    onyen="basicstudent",
    first_name="Basic",
    last_name="Student",
    email="basicstudent@unc.edu",
    role=student_role
)

accommodation_student = StudentModel(
    onyen="accommodationstudent",
    first_name="Accommodation",
    last_name="Student",
    email="accommodationstudent@unc.edu",
    role=student_role,
    base_extra_time=timedelta(hours=2),
)

withdrawn_student = StudentModel(
    onyen="withdrawnstuent",
    first_name="Withdrawn",
    last_name="Student",
    email="withdrawnstudent@unc.edu",
    role=student_role,
    exit_date=datetime.now()
)

data = [
    basic_student,
    accommodation_student,
    withdrawn_student
]