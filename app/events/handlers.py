from fastapi_events.handlers.local import local_handler

from app.database import SessionLocal
from app.events import ModifyAssignmentCrudEvent

"""
NOTE: Use `get_db_persistent` instead of `get_db`. FastAPI-Events does not support generator-based DI.
You MUST call Session.close() once you are done with the database session. 
"""


@local_handler.register(event_name="crud:assignment:*")
async def handle_sync_create_assignment(event: ModifyAssignmentCrudEvent):
    from app.services import GiteaService, CourseService
    
    event_name, payload = event
    assignment = payload["assignment"]

    with SessionLocal() as session:
        course_service = CourseService(session)
        gitea_service = GiteaService(session)

        hook_content = await gitea_service.get_master_repo_prereceive_hook()    
        master_repository_name = await course_service.get_master_repository_name()
        instructor_organization_name = await course_service.get_instructor_gitea_organization_name()

        await GiteaService(session).set_git_hook(
            repository_name=master_repository_name,
            owner=instructor_organization_name,
            hook_id="pre-receive",
            hook_content=hook_content
        )