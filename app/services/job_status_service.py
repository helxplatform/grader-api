from uuid import UUID
from celery import Task
from sqlalchemy.orm import Session
from app.models.job_status import JobStatus, JobStatusModel

class JobStatusService:
    def __init__(self, session: Session):
        self.session = session

    def get_status_logs_for_job(self, job_id: str | UUID) -> list[JobStatusModel]:
        return self.session.query(JobStatusModel).filter_by(id=job_id).all()

    def get_singleton_job_status(self, job: str | Task) -> JobStatusModel | None:
        """ This takes the either the job name or the literal job function, as in decorated by @app.task(name='', ...) """
        job_name = job if isinstance(job, str) else job.name
        row = self.session.query(JobStatusModel) \
            .filter_by(type=job_name) \
            .order_by(JobStatusModel.status_date.desc()) \
            .limit(1) \
            .first()
        if row is None: return None
        if row.status == JobStatus.SUCCESS or row.status == JobStatus.FAILURE or row.status == JobStatus.REVOKED:
            # If the most recent status for the job is a completed status, then there is no task running currently.
            return None
        return row