import unittest
from unittest.mock import MagicMock, patch
from fastapi import Request
from datetime import datetime
from sqlalchemy.orm import Session

from app.api.api_v1.endpoints.student_router import router
from app.schemas import StudentSchema
from app.services import StudentService
from pydantic import BaseModel

class CreateStudentBody(BaseModel):
    onyen: str
    first_name: str
    last_name: str
    email: str

class TestStudentRouter(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_db = MagicMock(spec=Session)
        self.mock_student = StudentSchema(
            id=1, 
            onyen="test",
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            user_type="student",
            join_date=datetime.today()
        )

    @patch('app.api.api_v1.endpoints.student_router.StudentService')
    async def test_get_student(self, mock_student_service):
        # mock service calls
        async def get_user_by_onyen(onyen: str):
            return self.mock_student

        mock_student_service.return_value.get_user_by_onyen = get_user_by_onyen

        # call the endpoint function and assert the response
        response = await router.routes[0].endpoint(db=self.mock_db, onyen="test")
        self.assertEqual(response, self.mock_student)

    @patch('app.api.api_v1.endpoints.student_router.StudentService')
    async def test_list_students(self, mock_student_service):
        # mock service calls
        mock_students = [
            self.mock_student,
            StudentSchema(
                id=2, 
                onyen="jane",
                first_name="Jane",
                last_name="Doe",
                email="jane@example.com",
                user_type="student",
                join_date=datetime.today()
            )
        ]
        
        async def list_students():
            return mock_students
        
        mock_student_service.return_value.list_students = list_students

        # call the endpoint function and assert the response
        response = await router.routes[1].endpoint(db=self.mock_db)
        self.assertEqual(response, mock_students)

    @patch('app.api.api_v1.endpoints.student_router.StudentService')
    async def test_create_student_with_autogen_password(self, mock_student_service):
        mock_student_body = CreateStudentBody(
            onyen="test",
            first_name="John",
            last_name="Doe",
            email="john@email.com"
        )

        # mock service calls
        async def create_student(**kwargs):
            return self.mock_student
        mock_student_service.return_value.create_student = create_student
        
        # call the endpoint function and assert the response
        response = await router.routes[2].endpoint(db=self.mock_db, student_body = mock_student_body)
        self.assertEqual(response, self.mock_student)
        
suite = unittest.TestLoader().loadTestsFromTestCase(TestStudentRouter)
unittest.TextTestRunner(verbosity=2).run(suite)
