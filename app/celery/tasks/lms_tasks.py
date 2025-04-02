import asyncio
from datetime import timedelta
from celery_singleton import Singleton
from app.celery import celery_app
from app.database import SessionLocal
from app.services import LmsSyncService

# NOTE: Singleton defines a "singleton" task which can only enter the queue once at a time,
# so we can't end up with 2 downsync tasks simultaneously.
@celery_app.task(name="downsync", base=Singleton)
def downsync_task():
    with SessionLocal() as session:
        lms_sync_service = LmsSyncService(session)
        return asyncio.run(lms_sync_service.downsync())