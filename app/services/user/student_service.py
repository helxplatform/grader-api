from typing import List
from app.events import dispatch
from app.models import StudentModel
from app.events import CreateUserCrudEvent
from app.core.role_permissions import student_role
from app.core.exceptions import NotAStudentException, UserAlreadyExistsException, UserNotFoundException
from .user_service import UserService

class StudentService(UserService):
    async def list_students(
        self,
    ) -> List[StudentModel]:
        return self.session.query(StudentModel).all()

    async def create_student(
        self,
        onyen: str,
        name: str,
        email: str
    ) -> StudentModel:
        from app.services import GiteaService, CourseService, CleanupService, CollaboratorPermission

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

        student = StudentModel(
            onyen=onyen,
            name=name,
            email=email,
            role=student_role
        )
        self.session.add(student)
        self.session.commit()

        cleanup_service = CleanupService.User(self.session, student)

        try:
            password = await super().create_user_auto_password_auth(onyen)
        except Exception as e:
            await cleanup_service.undo_create_user(delete_database_user=True)
            raise e

        gitea_service = GiteaService(self.session)
        course_service = CourseService(self.session)

        master_repo_name = await course_service.get_master_repository_name()
        student_repo_name = await course_service.get_student_repository_name(onyen)
        instructor_organization = await course_service.get_instructor_gitea_organization_name()
        
        try:
            await gitea_service.create_user(onyen, email, password)
        except Exception as e:
            await cleanup_service.undo_create_user(delete_database_user=True, delete_password_secret=True)
            raise e
        
        try:
            await gitea_service.add_collaborator_to_repo(
                name=master_repo_name,
                owner=instructor_organization,
                collaborator_name=onyen,
                permission=CollaboratorPermission.READ
            )
            await gitea_service.fork_repository(
                name=master_repo_name,
                owner=instructor_organization,
                new_owner=onyen
            )
            # The remote is subject to change when renamed, so we don't use the remote returned by fork_repository.
            student.fork_remote_url = await gitea_service.modify_repository(
                name=master_repo_name,
                owner=onyen,
                new_name=student_repo_name
            )
            self.session.commit()

        except Exception as e:
            await cleanup_service.undo_create_user(delete_database_user=True, delete_password_secret=True, delete_gitea_user=True)
            raise e

        dispatch(CreateUserCrudEvent(user=student))

    async def get_user_by_onyen(self, onyen: str) -> StudentModel:
        user = await super().get_user_by_onyen(onyen)
        if not isinstance(user, StudentModel):
            raise NotAStudentException()
        return user
    
    async def set_fork_cloned(self, student: StudentModel) -> None:
        student.fork_cloned = True
        self.session.commit()

    async def get_total_students(self) -> int:
        return self.session.query(StudentModel).count()
