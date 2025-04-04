from uuid import UUID
from httpx import HTTPStatusError
from celery import Task
from sqlalchemy.orm import Session
from app.models import AssignmentModel, MasterNotebookRevisionModel
from app.core.exceptions import AssignmentNotebookRevisionNotFoundException, AssignmentNotebookRevisionNotSelectedException

class MasterNotebookRevisionService:
    def __init__(self, session: Session):
        self.session = session

    async def get_assignment_revision_by_path(
        self,
        assignment: AssignmentModel,
        master_notebook_path: str
    ) -> MasterNotebookRevisionModel:
        for revision in assignment.master_notebook_revisions:
            if revision.master_notebook_path == master_notebook_path:
                return revision
        raise AssignmentNotebookRevisionNotFoundException()

    # NOTE: This will only create and commit the revision for you, but nothing beyond that.
    # You must still explicitly assign the revision as the assignment's active revision, if desired.
    async def create_assignment_revision(
        self,
        assignment: AssignmentModel,
        master_notebook_path: str,
        master_notebook_content: str
    ) -> MasterNotebookRevisionModel:
        notebook_revision = MasterNotebookRevisionModel(
            assignment_id=assignment.id,
            master_notebook_path=master_notebook_path,
            master_notebook_content=master_notebook_content
        )
        self.session.add(notebook_revision)
        self.session.commit()

        return notebook_revision
    
    """ The master notebook itself is untracked and never committed; however, the student version
    is tracked/committed, which can be used to determine if the revision has been explicitly "published."
    
    This is relevant in that, while the master notebook's contents *can* be updated prior to committing,
    its contents must be finalized and immutable once the revision has been published to students
    (as a consequence of the merge policy).
    """
    async def get_revision_is_committed(
        self,
        assignment: AssignmentModel,
        # If unspecified, uses the active revision associated with the assignment.
        master_notebook_revision: MasterNotebookRevisionModel | None = None
    ) -> bool:
        from app.services import CourseService, GiteaService
        course_service = CourseService(self.session)
        gitea_service = GiteaService(self.session)

        if master_notebook_revision is None:
            if assignment.master_notebook_revision_id is None:
                raise AssignmentNotebookRevisionNotSelectedException()
            master_notebook_revision = assignment.active_master_notebook_revision

        master_repository_name = await course_service.get_master_repository_name()
        owner = await course_service.get_instructor_gitea_organization_name()
        branch_name = await course_service.get_master_branch_name()

        # NOTE: If the assignment is manually graded, then the master notebook path is actually tracked and distributed to students.
        if assignment.manual_grading:
            assignment_notebook_full_path = f"{ assignment.directory_path}/{ master_notebook_revision.master_notebook_path }"
        else:
            assignment_notebook_full_path = f"{ assignment.directory_path }/{ master_notebook_revision.student_notebook_path }"

        try:
            await gitea_service.get_file_contents(
                name=master_repository_name,
                owner=owner,
                path=assignment_notebook_full_path,
                treeish_id=branch_name
            )
            return True
        except HTTPStatusError as e:
            if e.response.status_code == 404:
                return False
            
            raise e