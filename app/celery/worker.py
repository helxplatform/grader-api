import json
from redis import Redis
from celery import Celery
from celery.result import AsyncResult
from app.core.config import settings

redis_client = Redis.from_url(settings.CELERY_BROKER_URI)
celery_app = Celery(
    __name__,
    broker=settings.CELERY_BROKER_URI,
    backend=settings.CELERY_RESULT_BACKEND,
    result_extended=True
)
celery_app.conf.update(
    imports=["app.celery.tasks"],
    broker_connection_retry_on_startup=True,
    task_track_started=True,
    worker_enable_remote_control=True,
    beat_schedule={
        "periodic-downsync": {
            "task": "downsync",
            "schedule": 60
        }
    }
)

def get_task_ids_by_name(
    task_name: str,
    # Currently running tasks
    include_active=True,
    # Reserved by a worker to run, but not running yet
    include_reserved=True,
    # Scheduled to run by a worker at some point in the future, but not running yet
    include_scheduled=True,
    # Entered into the broker queue but not yet picked up by a worker
    include_pending=True
) -> list[str]:
    inspect = celery_app.control.inspect()
    tasks = {}
    if include_active: tasks += inspect.active()
    if include_reserved: tasks += inspect.reserved()
    if include_scheduled: tasks += inspect.scheduled()

    task_ids = [task["id"] for task in tasks.values() if task["name"] == task_name]

    # Load pending tasks (still in queue)
    if include_pending:
        for item in redis_client.lrange("celery", 0, -1):
            task_data = json.loads(item)
            if task_data.get("headers", {}).get("task") == task_name:
                task_id = task_data["headers"].get("id")
                if task_id is not None: task_ids.append(task_id)

    return task_ids

def get_task_result_by_id(task_id: str) -> AsyncResult:
    return celery_app.AsyncResult(task_id)

def revoke_task_by_id(task_id: str, terminate=False):
    kill_kwargs = { "terminate": True, "signal": "SIGTERM" } if terminate else {}
    celery_app.control.revoke(task_id, **kill_kwargs)

def dangerous_forcekill_task_by_id(task_id: str):
    """ NOTE: Be VERY careful about sending a SIGKILL to a running task.
    It's unlikely but possible to cause situations where state consistency
    is not recovered before termination (e.g., a task is killed after inserting some
    row into the DB, but before it can propagate it to Gitea). 
    """
    celery_app.control.revoke(task_id, terminate=True, signal="SIGKILL")