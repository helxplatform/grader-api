import unittest
from unittest import mock
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from app.services.user.student_service import StudentService  # Adjust the import based on your actual structure
from app.models import StudentModel
from app.core.exceptions import NotAStudentException, UserAlreadyExistsException, UserNotFoundException

class TestStudentService(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.mock_session = MagicMock(spec=Session)
        self.student_service = StudentService(self.mock_session)

    async def test_list_students(self):
        # Mock the session.query().all() method
        with patch.object(self.student_service.session.query(StudentModel), 'all') as mock_query_all:
            mock_query_all.return_value = [StudentModel(id=1, onyen='test', first_name='Test', last_name='Student', email='test@student.com')]

            result = await self.student_service.list_students()
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], StudentModel)

    async def test_create_student_user_already_exists(self):
         # Mock necessary methods and services
        with patch('app.services.CourseService') as mock_course_service, \
             patch('app.services.GiteaService', autospec=True) as mock_gitea_service, \
             patch.object(self.student_service.session, 'commit') as mock_commit:
            # Mock CourseService.get_master_repository_name and CourseService.get_instructor_gitea_organization_name
            mock_course_service.return_value.get_master_repository_name.return_value = 'master_repo'
            mock_course_service.return_value.get_instructor_gitea_organization_name.return_value = 'instructor_org'

            # Mock UserService.get_user_by_onyen and UserService.get_user_by_email to simulate non-existing users
            self.student_service.get_user_by_onyen = unittest.mock.AsyncMock(side_effect=UserAlreadyExistsException)
            self.student_service.get_user_by_email = unittest.mock.AsyncMock(side_effect=UserAlreadyExistsException)

            # Mock GiteaService.create_user and GiteaService.fork_repository
            mock_gitea_service.return_value.create_user = unittest.mock.AsyncMock(return_value=None)
            mock_gitea_service.return_value.fork_repository = unittest.mock.AsyncMock(return_value=None)

            with self.assertRaises(UserAlreadyExistsException):
                await self.student_service.create_student(
                    onyen='test',
                    first_name='Test',
                    last_name='Student',
                    email='test@student.com'
                )

suite = unittest.TestLoader().loadTestsFromTestCase(TestStudentService)
unittest.TextTestRunner(verbosity=2).run(suite)
