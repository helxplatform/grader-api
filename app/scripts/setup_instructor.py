import asyncio
from app.database import SessionLocal
from app.services import InstructorService
from app.core.exceptions import UserAlreadyExistsException

async def create_instructor(onyen: str, first_name: str, last_name: str, email: str):
    session = SessionLocal()
    await InstructorService(session).create_instructor(
        onyen=onyen,
        first_name=first_name,
        last_name=last_name,
        email=email
    )
    session.close()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("Create an instructor/credential secret in the database")
    parser.add_argument(
        "--onyen",
        type=str,
        required=True,
        help="Instructor's onyen"
    )
    parser.add_argument(
        "--first_name",
        type=str,
        required=True,
        help="Instructor's first name"
    )
    parser.add_argument(
        "--last_name",
        type=str,
        required=True,
        help="Instructor's last name"
    )
    parser.add_argument(
        "--email",
        type=str,
        required=True,
        help="Instructor's email"
    )

    args = parser.parse_args()

    try:
        asyncio.run(create_instructor(
            onyen=args.onyen,
            first_name=args.first_name,
            last_name=args.last_name,
            email=args.email
        ))
        print(f"Successfully created instructor: {args.onyen}")
    except UserAlreadyExistsException:
        print("Instructor already exists, skipping...")
    