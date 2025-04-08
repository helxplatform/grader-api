from fastapi import APIRouter, Request, Depends, Header
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.core.config import settings
from app.schemas import SettingsSchema

router = APIRouter()

@router.get("/settings", response_model=SettingsSchema)
def get_settings(
    *,
    db: Session = Depends(get_db)
):
    return SettingsSchema(
        gitea_ssh_url=settings.GITEA_SSH_URL,
        documentation_url=settings.DOCUMENTATION_URL
    )