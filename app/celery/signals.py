import inspect
import asyncio
from celery.signals import (
    task_received, task_internal_error, task_revoked,
    task_success, task_failure, task_retry, task_prerun
)
from celery_singleton.util import generate_lock
from celery_singleton.config import Config
from celery_singleton.backends import get_backend
from app.celery.worker import celery_app
from app.database import SessionLocal
from app.services import WebsocketManagerService, JobStatusService, InstructorService
from app.models.job_status import JobStatusModel, JobStatus
from app.schemas import JobSchema, WebsocketJobStatusMessage

def handle_job_status_update(job_id: str, job_type: str | None, job_status: JobStatus) -> None:
    """ Store a job status update in the database and dispatch a websocket event. """
    async def _handle_job_status_update():
        with SessionLocal() as session:
            job_status_model = JobStatusService(session).create_job_status_update(job_id, job_type, job_status)
            ws_message = WebsocketJobStatusMessage(
                data=JobSchema.from_orm(job_status_model)
            )
            
            if job_type == "downsync":
                user_list = await InstructorService(session).list_instructors()
            else:
                user_list = []

            WebsocketManagerService.publish_sync_pubsub_ws_message(ws_message, user_list)
    
    asyncio.run(_handle_job_status_update())

@task_received.connect
def task_received_handler(request, **kw):
    handle_job_status_update(request.task_id, request.task_name, JobStatus.RECEIVED)

@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, **kw):
    handle_job_status_update(task_id, sender.name, JobStatus.STARTED)

@task_success.connect
def task_success_handler(sender=None, result=None, **kw):
    handle_job_status_update(sender.request.id, sender.name, JobStatus.SUCCESS)

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, **kw):
    handle_job_status_update(task_id, sender.name, JobStatus.FAILURE)

@task_internal_error.connect
def task_internal_error_handler(sender=None, task_id=None, **kw):
    handle_job_status_update(task_id, sender.name, JobStatus.FAILURE)

@task_retry.connect
def task_retry_handler(sender=None, request=None, **kw):
    handle_job_status_update(request.task_id, request.task_name, JobStatus.RETRY)

@task_revoked.connect
def task_revoked_handler(sender=None, request=None, **kw):
    handle_job_status_update(request.task_id, request.task_name, JobStatus.REVOKED)

""" Source: https://github.com/steinitzu/celery-singleton/issues/29 """
@task_revoked.connect
def clean_singleton_lock_on_revoke(sender=None, request=None, reason=None, **kwargs):
    """ For some reason, Celery devs decided to remove basically every task workflow callback,
    including on_revoked, which means that celery-singleton has no idea if a task is revoked.
    We need to manally fix this here...
    """
    task_id = request.id
    task_name = request.task
    task_args = request.args
    task_kwargs = request.kwargs

    func = celery_app.tasks[task_name]
    unique_on = getattr(func, "unique_on", None)

    # Not a singleton task, can ignore...
    if not hasattr(func, "_singleton_backend"): return

    if unique_on:
        if isinstance(unique_on, str):
            unique_on = [unique_on]
        sig = inspect.signature(func)
        bound = sig.bind(*task_args, **task_kwargs).arguments

        unique_args = []
        unique_kwargs = {key: bound[key] for key in unique_on}
    else:
        unique_args = task_args
        unique_kwargs = task_kwargs

    app_config = Config(celery_app)
    backend = get_backend(app_config)
    redis_key = generate_lock(task_name,
                              task_args=unique_args,
                              task_kwargs=unique_kwargs,
                              key_prefix=app_config.key_prefix)

    # clean lock
    cache_task_id = backend.get(redis_key)
    if cache_task_id and cache_task_id.startswith(task_id):
        print(f"Cleaning singletion lock: {redis_key}, task_id: {task_id}")
        backend.clear(redis_key)
