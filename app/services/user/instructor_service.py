from typing import List
from app.events import dispatch
from app.models import InstructorModel
from app.events import CreateUserCrudEvent
from app.core.role_permissions import instructor_role
from app.core.exceptions import NotAnInstructorException, UserAlreadyExistsException, UserNotFoundException
from .user_service import UserService

class InstructorService(UserService):
    async def list_instructors(self) -> List[InstructorModel]:
        return self.session.query(InstructorModel).all()

    async def create_instructor(
        self,
        onyen: str,
        name: str,
        email: str
    ) -> InstructorModel:
        from app.services import GiteaService, CourseService, CleanupService

        try:
            await super().get_user_by_onyen(onyen)
            raise UserAlreadyExistsException()
        except UserNotFoundException:
            pass
        
        try:
            await super().get_user_by_email(email)
            raise UserAlreadyExistsException()
        except UserNotFoundException:
            pass

        instructor = InstructorModel(
            onyen=onyen,
            name=name,
            email=email,
            role=instructor_role
        )
        self.session.add(instructor)
        self.session.commit()

        cleanup_service = CleanupService.User(self.session, instructor)

        try:
            password = await super().create_user_auto_password_auth(onyen)
        except Exception as e:
            await cleanup_service.undo_create_user(delete_database_user=True)
            raise e

        gitea_service = GiteaService(self.session)
        course_service = CourseService(self.session)

        instructor_org_name = await course_service.get_instructor_gitea_organization_name()
        try:
            await gitea_service.create_user(onyen, email, password)
        except Exception as e:
            await cleanup_service.undo_create_user(delete_database_user=True, delete_password_secret=True)
            raise e
        
        try:
            await gitea_service.add_user_to_organization(instructor_org_name, onyen)
        except Exception as e:
            await cleanup_service.undo_create_user(delete_database_user=True, delete_password_secret=True, delete_gitea_user=True)
            raise e

        dispatch(CreateUserCrudEvent(user=instructor))

    async def get_user_by_onyen(self, onyen: str) -> InstructorModel:
        user = await super().get_user_by_onyen(onyen)
        if not isinstance(user, InstructorModel):
            raise NotAnInstructorException()
        return user