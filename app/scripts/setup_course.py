import asyncio
from app.database import SessionLocal
from app.services import CourseService
from app.core.exceptions import CourseAlreadyExistsException

async def create_course(name: str):
    session = SessionLocal()
    course_service = CourseService(session)

    await course_service.create_course(
        course_name=name
    )

    session.close()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("Setup the course in the database")
    parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="Course name"
    )

    args = parser.parse_args()

    try:
        asyncio.run(create_course(
            name=args.name
        ))
        print(f"Successfully created course: {args.name}")
    except CourseAlreadyExistsException:
        print("Course already exists, exiting gracefully...")