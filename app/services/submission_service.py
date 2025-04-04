import os.path
import tempfile
from typing import List
from pathlib import Path
from datetime import datetime
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from app.events import event_emitter
from app.models import StudentModel, AssignmentModel, SubmissionModel, MasterNotebookRevisionModel
from app.schemas import SubmissionSchema, DatabaseSubmissionSchema, SubmissionCrudEvent, CrudType
from app.core.exceptions import (
    SubmissionNotFoundException,
    AssignmentNotebookRevisionNotFoundException, AssignmentNotebookRevisionNotSelectedException
)
from app.core.utils.datetime import get_now_with_tzinfo

class SubmissionService:
    def __init__(self, session: Session):
        self.session = session

    async def create_submission(
        self,
        student: StudentModel,
        assignment: AssignmentModel,
        commit_id: str
    ) -> SubmissionModel:
        from app.services import StudentAssignmentService, CourseService

        # TODO: We should validate that the submitted commit id actually exists in gitea before persisting it in the database.
        # We don't want another component of EduHeLx to assume the commit we return exists and crash when it doesn't.
        # Alternatively, we could bake this logic into the endpoints to get submissions, rather than into this one.

        course = await CourseService(self.session).get_course()


        # Assert the assignment can be submitted to by the student.
        await StudentAssignmentService(self.session, student, assignment, course).validate_student_can_submit()

        submission = SubmissionModel(
            student_id=student.id,
            assignment_id=assignment.id,
            commit_id=commit_id,
            master_notebook_revision_id=assignment.master_notebook_revision_id
        )

        self.session.add(submission)
        self.session.commit()

        try:
            await event_emitter.emit_async(SubmissionCrudEvent(resource=submission, crud_type=CrudType.CREATE))
        except: pass

        return submission
    
    async def get_submission_by_id(
        self,
        submission_id: int
    ) -> SubmissionModel:
        submission = self.session.query(SubmissionModel) \
            .filter_by(id=submission_id) \
            .first()
        if submission is None:
            raise SubmissionNotFoundException()
        return submission

    async def get_submissions(
        self,
        student: StudentModel,
        assignment: AssignmentModel,
        # If specified, only list submissions for a particular revision of the assignment notebook.
        master_notebook_revision: MasterNotebookRevisionModel | None = None
    ) -> List[SubmissionModel]:
        
        query = self.session.query(SubmissionModel) \
            .filter_by(student_id=student.id, assignment_id=assignment.id) \
            .order_by(desc(SubmissionModel.submission_time)) \
            
        if master_notebook_revision is not None:
            query = query.filter_by(master_notebook_revision_id=master_notebook_revision.id)
            
        submissions = query.all()

        return submissions

    async def get_active_submission(
        self,
        student: StudentModel,
        assignment: AssignmentModel,
        # When unspecified, the active notebook revision will be used.
        master_notebook_revision: MasterNotebookRevisionModel | None = None
    ) -> SubmissionModel:
        if master_notebook_revision is None:
            if assignment.master_notebook_revision_id is None:
                raise AssignmentNotebookRevisionNotSelectedException()
            master_notebook_revision = assignment.active_master_notebook_revision
            
        submission = self.session.query(SubmissionModel) \
            .filter_by(
                student_id=student.id,
                assignment_id=assignment.id,
                master_notebook_revision_id=master_notebook_revision.id
            ) \
            .order_by(desc(SubmissionModel.submission_time)) \
            .limit(1) \
            .first()
        
        if submission is None:
            raise SubmissionNotFoundException()
        
        return submission
        
    """ NOTE: Marked for refactor. Not a fan of this workflow... """
    async def get_current_submission_attempt(
        self,
        student: StudentModel,
        assignment: AssignmentModel,
        # If specified, return the current submission attempt for the specified revision.
        # NOTE: This may have consequences e.g. on Canvas' end where assignments do not have
        # any notion of attempts on a per-revision basis.
        master_notebook_revision: MasterNotebookRevisionModel | None = None
    ) -> int:
        query = self.session.query(SubmissionModel) \
            .filter(SubmissionModel.assignment_id == assignment.id) \
            .filter(SubmissionModel.student_id == student.id)
        
        if master_notebook_revision is not None:
            query = query.filter_by(master_notebook_revision_id=master_notebook_revision.id)

        return query.count()
        
    async def get_submission_schema(self, submission: SubmissionModel) -> SubmissionSchema:
        submission_schema = DatabaseSubmissionSchema.from_orm(submission).dict()
        submission_schema["active"] = await self.get_active_submission(submission.student, submission.assignment) == submission
        
        return SubmissionSchema(**submission_schema)
