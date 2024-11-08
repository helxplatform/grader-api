from app.database import SessionLocal
from app.schemas import CrudEvent, AssignmentCrudEvent, ResourceType
from app.events.emitter import event_emitter

"""
NOTE: Keep in mind that exceptions raised in event handlers bubble up to the original emitter.
If it's expected that the handler may fail, then the handler should catch the failure instead of
raising it to the dispatcher (since this will in most cases bubble to the calling service method).
"""

@event_emitter.on("crud")
async def update_master_repo_hook(crud_event: CrudEvent):
    """ Update the master repo's pre-receive hook whenever an assignment is changed. """
    from app.services import GiteaService, StudentService, CourseService
    
    if not isinstance(crud_event, AssignmentCrudEvent): return
    
    assignment = crud_event.resource
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

@event_emitter.on("crud")
async def publish_crud_operation(event: CrudEvent):
    """ Publish a Websocket event indicating the crud operation. """
    from app.services import (
        WebsocketManagerService, CourseService,
        UserService, StudentService, InstructorService,
        StudentAssignmentService, InstructorAssignmentService
    )
    from app.models import (
        AssignmentModel, CourseModel, SubmissionModel,
        UserModel, StudentModel, InstructorModel
    )
    from app.models.user import UserType
    from app.schemas import WebsocketCrudMessage


    with SessionLocal() as session:
        def get_crud_ws_message(resource_id: int) -> WebsocketCrudMessage:
            return WebsocketCrudMessage.from_crud_event(event, resource_id)

        user_service = UserService(session)
        student_service = StudentService(session)
        instructor_service = InstructorService(session)

        all_users = await user_service.list_users()
        students = [u for u in all_users if isinstance(u, StudentModel)]
        instructors = [u for u in all_users if isinstance(u, InstructorModel)]

        if event.resource_type == ResourceType.COURSE:
            """ The course is a fully public resource, thus anyone can receive this event. """
            course_model: CourseModel = event.resource

            await WebsocketManagerService.publish_pubsub_ws_message(get_crud_ws_message(course_model.id), all_users)
        
        elif event.resource_type == ResourceType.ASSIGNMENT:
            """ At the moment, this is also a fully public resource. We don't hide unpublished assignments
            from students currently. This may be subject to change in the future.
            """
            assignment_model: AssignmentModel = event.resource

            await WebsocketManagerService.publish_pubsub_ws_message(get_crud_ws_message(assignment_model.id), all_users)

        elif event.resource_type == ResourceType.USER:
            """ User events are fully visible to instructors and the user whom the event concerns.
            If the event is related to an instructor user, then it is also visible to all students.
            """
            user_model: UserModel = event.resource

            visible_users = set([*instructors, user_model])
            if isinstance(user_model, InstructorModel):
                # When the event concerns an instructor user, it is also visible to all students.
                visible_users.update(students)

            await WebsocketManagerService.publish_pubsub_ws_message(get_crud_ws_message(user_model.id), visible_users)

        elif event.resource_type == ResourceType.SUBMISSION:
            """ This is fully public to instructors and also to the student who owns the submission. """
            submission_model: SubmissionModel = event.resource

            visible_users = [*instructors, submission_model.student]
            await WebsocketManagerService.publish_pubsub_ws_message(get_crud_ws_message(submission_model.id), visible_users)