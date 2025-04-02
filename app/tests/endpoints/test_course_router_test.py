import unittest
from fastapi import Request
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from app.main import app
from app.api.api_v1.endpoints.course_router import router
from app.schemas.user import InstructorSchema
from app.schemas import CourseWithInstructorsSchema
from app.core.dependencies import PermissionDependency, CourseListPermission, InstructorListPermission
from sqlalchemy.orm import Session

class TestCourseEndpoints(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.mock_db = MagicMock(spec=Session)
        self.client = TestClient(router)

    async def test_get_course(self):
        # Create a test client using the router

        # Mock the dependencies
        mock_request = MagicMock(spec=Request)

        mock_course = MagicMock()
        mock_course.name = "Test Course"
        mock_course.master_remote_url = "http://example.com"
        mock_course.instructors = ["Instructor 1", "Instructor 2"]

        # Mock the CourseService and specify its return value
        with patch('app.services.course_service.CourseService') as mock_course_service:
            mock_course_service.return_value.get_course_with_instructors_schema.return_value = mock_course

            # Call the endpoint function with the mocked dependencies
            response = await router.routes[0].endpoint(db=self.mock_db, request=mock_request)

        # Assertions
        self.assertEqual(response, mock_course)
        mock_course_service.return_value.get_course_with_instructors_schema.assert_called_once_with()


suite = unittest.TestLoader().loadTestsFromTestCase(TestCourseEndpoints)
unittest.TextTestRunner(verbosity=2).run(suite)
