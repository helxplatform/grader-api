import unittest
import httpx
from unittest.mock import patch, AsyncMock, MagicMock
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from app.services import CourseService
from app.models import CourseModel, InstructorModel
from app.services.user import InstructorService
from tests.data.database.course import data
from app.schemas import CourseWithInstructorsSchema
from app.core.exceptions import (
    MultipleCoursesExistException,
    NoCourseExistsException,
    CourseAlreadyExistsException
)

async def async_mock(*args, **kwargs):
    pass

class TestCourseService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_session = MagicMock(spec=Session)

        self.course_service = CourseService(session=self.mock_session)
        self.mock_course = CourseModel(name="COMP 555", master_remote_url="")

    async def test_get_course_single_result(self):
        self.mock_session.query().one.return_value = self.mock_course
        result = await self.course_service.get_course()

        self.assertIsInstance(result, CourseModel)
        self.assertEqual(result, self.mock_course)
    
    async def test_get_course_multiple_results(self):
        self.mock_session.query().one.side_effect = MultipleResultsFound()

        with self.assertRaises(MultipleCoursesExistException):
            self.assertRaises(await self.course_service.get_course())

    async def test_get_course_no_result(self):
        self.mock_session.query().one.side_effect = NoResultFound()

        with self.assertRaises(NoCourseExistsException):
            self.assertRaises(await self.course_service.get_course())
    
    async def test_get_course_with_instructors_schema_success(self):
        mock_course = CourseModel(id=1, name="Math", master_remote_url="http://example.com")
        instructorList = [InstructorModel(id=1, onyen="instructor_onyen", first_name="Ins", last_name="Tructor", email="email@unc.com")]

        self.mock_session.query().one.return_value = mock_course
        self.mock_session.query().all.return_value = instructorList

        expected_course = CourseModel(id=1, name="Math", master_remote_url="http://example.com")
        expected_course.instructors=instructorList

        result = await self.course_service.get_course_with_instructors_schema()
        expected_result = CourseWithInstructorsSchema.from_orm(expected_course)

        self.assertEqual(result, expected_result)

    async def test_get_instructor_gitea_organization_name(self):
        self.mock_session.query().one.return_value = self.mock_course

        result = await self.course_service.get_instructor_gitea_organization_name()
        assert result == "COMP 555-instructors"

    async def test_get_master_repository_name(self):
        self.mock_session.query().one.return_value = self.mock_course

        result = await self.course_service.get_master_repository_name()
        assert result == "COMP 555-class-master-repo"

    async def test_create_course_fail(self):
        self.mock_session.query().one.return_value = self.mock_course

        with self.assertRaises(CourseAlreadyExistsException):
            self.assertRaises(await self.course_service.create_course(course_name="Math"))

    async def test_create_course_success(self):
        self.mock_session.query().one.side_effect = NoResultFound()
        self.mock_session.add.return_value = None
        self.mock_session.commit.return_value = None

        with patch('app.services.GiteaService') as mock_gitea_service:
            mock_gitea_service.return_value.create_organization = AsyncMock()
            mock_gitea_service.return_value.create_repository = AsyncMock(return_value="http://example.com")

            master_repository_name = f"{self.mock_course.name}-class-master-repo"
            instructor_organization = f"{self.mock_course.name}-instructors"

            result = await self.course_service.create_course(course_name=self.mock_course.name)        
            mock_gitea_service.return_value.create_organization.assert_called_with(instructor_organization)
            mock_gitea_service.return_value.create_repository.assert_called_with(name=master_repository_name, description=f"The class master repository for {self.mock_course.name}", owner=instructor_organization, private=False)
            
            self.mock_session.add.assert_called_once()
            self.mock_session.commit.assert_called_once()
            self.assertEqual(result.name, self.mock_course.name)
            self.assertEqual(result.master_remote_url, "http://example.com")

suite = unittest.TestLoader().loadTestsFromTestCase(TestCourseService)
unittest.TextTestRunner(verbosity=2).run(suite)
