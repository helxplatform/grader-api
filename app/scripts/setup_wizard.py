from app.database import SessionLocal
from app.services import CourseService
from app.services import InstructorService
from app.core.config import settings
from scripts import setup_course, setup_instructor

async def setup_wizard_has_ran() -> bool:
    with SessionLocal() as session:
        try:
            await CourseService(session).get_course()
            return True
        except: pass

    return False

async def run():
    data = settings.SETUP_WIZARD_DATA
    if data is None:
        raise ValueError("Data not configured for setup wizard")

    if setup_wizard_has_ran():
        raise ValueError("Setup wizard has already ran, skipping...")
    
    setup_course.create_course(data.course.name)
    for instructor in data.instructors:
        setup_instructor.create_instructor(
            onyen=instructor.onyen,
            first_name=instructor.first_name,
            last_name=instructor.last_name,
            email=instructor.email
        )