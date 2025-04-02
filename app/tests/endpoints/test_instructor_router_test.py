from typing import List
import unittest
from unittest.mock import MagicMock, patch
from pydantic import BaseModel

from sqlalchemy.orm import Session
from app.api.api_v1.endpoints.instructor_router import router
from app.schemas import InstructorSchema
from app.services import InstructorService
from app.core.dependencies import get_db, PermissionDependency, InstructorListPermission, InstructorCreatePermission

class CreateInstructorBody(BaseModel):
    onyen: str
    first_name: str
    last_name: str
    email: str

class TestInstructorRouter(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_db = MagicMock(spec=Session)
        self.mock_instructor = InstructorSchema(
            id=1, 
            onyen="test",
            first_name="John",
            last_name="Doe",
            email="instructor@email.com",
            user_type="instructor"
        )

    @patch('app.api.api_v1.endpoints.instructor_router.InstructorService')
    async def test_get_instructor(self, mock_instructor_service):
        # mock service calls
        async def get_user_by_onyen(onyen: str):
            return self.mock_instructor
        
        mock_instructor_service.return_value.get_user_by_onyen = get_user_by_onyen

        # call the endpoint function and assert the response
        response = await router.routes[0].endpoint(db=self.mock_db, onyen="test")
        self.assertEqual(response, self.mock_instructor)

    @patch('app.api.api_v1.endpoints.instructor_router.InstructorService')
    async def test_list_instructor(self, mock_instructor_service):
        # mock service calls
        mock_instructors = [
            self.mock_instructor,
            InstructorSchema(
                id=2, 
                onyen="jane",
                first_name="Jane",
                last_name="Doe",
                email="instructor-jane@email.com",
                user_type="instructor"
            )
        ]

        # mock service calls
        async def list_instructors():
            return mock_instructors
        mock_instructor_service.return_value.list_instructors = list_instructors

        # call the endpoint function and assert the response
        response = await router.routes[1].endpoint(db=self.mock_db)
        self.assertEqual(response, mock_instructors)

    @patch('app.api.api_v1.endpoints.instructor_router.InstructorService')
    async def test_create_instructor(self, mock_instructor_service):
        mock_instructor_body = CreateInstructorBody(
            onyen="test",
            first_name="John",
            last_name="Doe",
            email="john@email.com"
        )

        # mock service calls
        async def create_instructor(**kwargs):
            return self.mock_instructor
        mock_instructor_service.return_value.create_instructor = create_instructor

        # call the endpoint function and assert the response
        response = await router.routes[2].endpoint(db=self.mock_db, instructor_body=mock_instructor_body)
        self.assertEqual(response, self.mock_instructor)

suite = unittest.TestLoader().loadTestsFromTestCase(TestInstructorRouter)
unittest.TextTestRunner(verbosity=2).run(suite)
