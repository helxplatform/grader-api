from fastapi import APIRouter


router = APIRouter()

@router.get("/health/live", response_model=None, status_code=200)
async def heathcheckLive():
  pass

@router.get("/health/ready", response_model=None, status_code=200)
async def heathcheckReady():
  # In the future, check the health of redis and other internal systems here
  pass