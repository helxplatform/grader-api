from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import AssignmentOverrideModel
from app.enums.assignment_status import AssignmentStatus

class AssignmentOverrideService:
    def __init__(self, session: Session):
        self.session = session

    async def create_assignment_override(
        self,
        override: dict | None,
        student_id: int
    ) -> AssignmentOverrideModel:


        assignment_override = AssignmentOverrideModel(
            id=override["id"],
            student_id=student_id,
            assignment_id=override["assignment_id"],
            available_date=override["unlock_at"],
            due_date=override["due_at"]
        )

        self.session.add(assignment_override)
        self.session.commit()

        return assignment_override
    
    async def get_assignment_overrides_by_id(
        self,
        override_id: int
    ) -> list[AssignmentOverrideModel]:
        return self.session.query(AssignmentOverrideModel) \
            .filter_by(id=override_id) \
            .all()
    
    async def get_assignment_override_by_student(
        self,
        assignment_id: int,
        student_id: int
    ) -> AssignmentOverrideModel:
        return self.session.query(AssignmentOverrideModel) \
            .filter_by(assignment_id=assignment_id) \
            .filter_by(student_id=student_id) \
            .first()
    
    async def update_assignment_override(
        self,
        db_override: AssignmentOverrideModel,
        canvas_override: dict
    ) -> AssignmentOverrideModel:
        db_override.available_date = canvas_override["unlock_at"]
        db_override.due_date = canvas_override["due_at"]
        self.session.commit()
        return db_override
       