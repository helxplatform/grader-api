from datetime import datetime, timedelta, date
import json
import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from app.services import AssignmentService
from app.models import AssignmentModel
from app.schemas import UpdateAssignmentSchema
from app.core.exceptions import AssignmentNotFoundException

class TestAssignmentService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # I.e. available_date in FUTURE
        created_not_available_assignment = AssignmentModel(
            name="created_not_available",
            directory_path="/created_not_available",
            available_date=datetime.now() + timedelta(hours=2),
            due_date=datetime.now() + timedelta(hours=4)
        )

        # I.e. available_date in PAST
        # NOTE: An available assignment can also be closed, and being closed takes precedence.
        available_assignment = AssignmentModel(
            name="available",
            directory_path="/available",
            available_date=datetime.now() + timedelta(hours=-2),
            due_date=datetime.now() + timedelta(hours=2)
        )

        self.assignment_data = {
            "unavialable": created_not_available_assignment,
            "available": available_assignment,
        }
        
        self.mock_session = MagicMock()
        self.assignment_service = AssignmentService(session=self.mock_session)

    async def test_get_assignment_by_id_success(self):
        mock_assignment = self.assignment_data["unavialable"]
        mock_assignment_2 = self.assignment_data["available"]

        self.mock_session.query().filter_by().first.return_value = mock_assignment
        result_1 = await self.assignment_service.get_assignment_by_id(id=1)

        self.mock_session.query().filter_by().first.return_value = mock_assignment_2
        result_2 = await self.assignment_service.get_assignment_by_id(id=2)
        
        self.assertEqual(result_1, mock_assignment)
        self.assertEqual(result_2, mock_assignment_2)


    async def test_get_assignment_by_id_not_found(self):
        self.mock_session.query().filter_by().first.return_value = None

        with self.assertRaises(AssignmentNotFoundException):
            await self.assignment_service.get_assignment_by_id(id=1)

    async def test_get_assignments_success(self):
        mock_assignments = [
            self.assignment_data["available"],
            self.assignment_data["unavialable"]
        ]
        self.mock_session.query().all.return_value = mock_assignments

        result = await self.assignment_service.get_assignments()
        
        self.assertEqual(len(result), len(mock_assignments))
        self.assertEqual(result[0].name, mock_assignments[0].name)
        self.assertEqual(result[1].name, mock_assignments[1].name)

    async def test_get_assignment_by_name_success(self):
        mock_assignment = self.assignment_data["available"]
        self.mock_session.query().filter_by().first.return_value = mock_assignment

        result = await self.assignment_service.get_assignment_by_name(name="available")
        
        self.assertEqual(result.name, mock_assignment.name)

    async def test_get_assignment_by_name_not_found(self):
        self.mock_session.query().filter_by().first.return_value = None

        with self.assertRaises(AssignmentNotFoundException):
            await self.assignment_service.get_assignment_by_name(name="available")

    @patch('app.services.assignment_service.func.current_timestamp')
    async def test_update_assignment_name(self, mock_current_timestamp):
        mock_assignment = self.assignment_data["available"]
        self.mock_session.commit.return_value = None
        mock_current_timestamp.return_value = date.today()

        payload = UpdateAssignmentSchema(name="new_name")
        result = await self.assignment_service.update_assignment(assignment=mock_assignment, update_assignment=payload)
        
        self.assertEqual(result.name, "new_name")
        self.assertEqual(result.last_modified_date, date.today())
    
    @patch('app.services.assignment_service.func.current_timestamp')
    async def test_update_assignment_directory_path(self, mock_current_timestamp):
        mock_assignment = self.assignment_data["available"]
        self.mock_session.commit.return_value = None
        mock_current_timestamp.return_value = date.today()

        payload = UpdateAssignmentSchema(directory_path="new/directory/path")
        result = await self.assignment_service.update_assignment(assignment=mock_assignment, update_assignment=payload)
        
        self.assertEqual(result.directory_path, "new/directory/path")
        self.assertEqual(result.last_modified_date, date.today())

    @patch('app.services.assignment_service.func.current_timestamp')
    async def test_update_assignment_available_date(self, mock_current_timestamp):
        mock_assignment = self.assignment_data["available"]
        self.mock_session.commit.return_value = None
        mock_current_timestamp.return_value = date.today()

        new_date = mock_assignment.available_date + timedelta(hours=3)
        payload = UpdateAssignmentSchema(available_date=new_date)
        result = await self.assignment_service.update_assignment(assignment=mock_assignment, update_assignment=payload)
        
        self.assertEqual(result.available_date, new_date)
        self.assertEqual(result.last_modified_date, date.today())

    @patch('app.services.assignment_service.func.current_timestamp')
    async def test_update_assignment_due_date(self, mock_current_timestamp):
        mock_assignment = self.assignment_data["available"]
        self.mock_session.commit.return_value = None
        mock_current_timestamp.return_value = date.today()

        new_date = mock_assignment.due_date + timedelta(hours=3)
        payload = UpdateAssignmentSchema(due_date=new_date)
        result = await self.assignment_service.update_assignment(assignment=mock_assignment, update_assignment=payload)
        
        self.assertEqual(result.due_date, new_date)
        self.assertEqual(result.last_modified_date, date.today())


suite = unittest.TestLoader().loadTestsFromTestCase(TestAssignmentService)
unittest.TextTestRunner(verbosity=2).run(suite)
