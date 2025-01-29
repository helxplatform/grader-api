from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import AssignmentModel, AssignmentOverrideModel, CourseModel, StudentModel
# from app.schemas import (
#     AssignmentSchema,
#     InstructorAssignmentSchema,
#     StudentAssignmentSchema,
#     UpdateAssignmentSchema,
#     AssignmentOverrideSchema,
#     StudentSchema,
#     CourseSchema
# )
from app.enums.assignment_status import AssignmentStatus
from app.services.submission_service import SubmissionService

class AssignmentOverrideService:
    def __init__(self, session: Session):
        self.session = session

    async def create_assignment_override(
        self,
        overrides: dict | None
    ) -> AssignmentOverrideModel:

        override_collections = []

        for override in overrides:
            for student_id in override["student_ids"]:

                assignment_override = AssignmentOverrideModel(
                    id=override["id"],
                    student_id=student_id,
                    assignment_id=override["assignment_id"],
                    available_date=override["unlock_at"],
                    due_date=override["due_at"]
                )

                self.session.add(assignment_override)
                self.session.commit()

                override_collections.append(assignment_override)

        return override_collections
       