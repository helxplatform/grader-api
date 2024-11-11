import inspect
from celery.signals import (
    task_received, task_internal_error, task_revoked,
    task_success, task_failure, task_retry, task_prerun
)
from celery_singleton.util import generate_lock
from celery_singleton.config import Config
from celery_singleton.backends import get_backend
from app.celery.worker import celery_app
from app.database import SessionLocal
from app.models.job_status import JobStatusModel, JobStatus

@task_received.connect
def task_received_handler(request, **kw):
    with SessionLocal() as session:
        session.add(JobStatusModel(
            id=request.task_id,
            type=request.task_name,
            status=JobStatus.RECEIVED
        ))
        session.commit()

@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, **kw):
    with SessionLocal() as session:
        session.add(JobStatusModel(
            id=task_id,
            type=sender.name,
            status=JobStatus.STARTED
        ))
        session.commit()

@task_success.connect
def task_success_handler(sender=None, result=None, **kw):
    with SessionLocal() as session:
        session.add(JobStatusModel(
            id=sender.request.id,
            type=sender.name,
            status=JobStatus.SUCCESS
        ))
        session.commit()

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, **kw):
    with SessionLocal() as session:
        session.add(JobStatusModel(
            id=task_id,
            type=sender.name,
            status=JobStatus.FAILURE
        ))
        session.commit()

@task_internal_error.connect
def task_internal_error_handler(sender=None, task_id=None, **kw):
    with SessionLocal() as session:
        session.add(JobStatusModel(
            id=task_id,
            type=sender.name,
            status=JobStatus.FAILURE
        ))
        session.commit()

@task_retry.connect
def task_retry_handler(sender=None, request=None, **kw):
    with SessionLocal() as session:
        session.add(JobStatusModel(
            id=request.task_id,
            type=request.task_name,
            status=JobStatus.RETRY
        ))
        session.commit()

@task_revoked.connect
def task_revoked_handler(sender=None, request=None, **kw):
    with SessionLocal() as session:
        session.add(JobStatusModel(
            id=request.task_id,
            type=request.task_name,
            status=JobStatus.REVOKED
        ))
        session.commit()

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
