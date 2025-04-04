from datetime import datetime
from pydantic import BaseModel, PositiveInt

from ._unset import UNSET

class MasterNotebookRevisionSchema(BaseModel):
    id: int
    master_notebook_path: str
    master_notebook_content: str
    created_date: datetime

    class Config:
        orm_mode = True

class UpdateMasterNotebookRevisionSchema(BaseModel):
    master_notebook_path: str
    master_notebook_content: str