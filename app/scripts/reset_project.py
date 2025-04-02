import asyncio
from app.services import *
from app.database import *
from app.models import *

async def main():
    with SessionLocal() as session:
        course_service = CourseService(session)
        instructor_service = InstructorService(session)
        student_service = StudentService(session)
        gitea_service = GiteaService(session)

        for instructor in await instructor_service.list_instructors():
            try:
                await instructor_service.delete_user(instructor)
            except Exception as e: print(e)

        for student in await student_service.list_students():
            try:
                await student_service.delete_user(student)
            except Exception as e: print(e)
        
        instructor_org = await course_service.get_instructor_gitea_organization_name()
        try:
            await gitea_service.delete_organization(instructor_org, purge=True)
            session.delete(await course_service.get_course())
            session.commit()
        except Exception as e: print(e)

        

if __name__ == "__main__":
    asyncio.run(main())