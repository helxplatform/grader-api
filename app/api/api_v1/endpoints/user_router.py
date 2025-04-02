""" User router should contain endpoints that are able to be generalized to a user, rather than a specific account type. """

from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from typing import Union
from app.schemas import StudentSchema, InstructorSchema
from app.services import UserService, LDAPService
from app.services.ldap_service import LDAPUserInfoSchema
from app.core.dependencies import get_db, PermissionDependency, UserIsSuperuserPermission, RequireLoginPermission


router = APIRouter()

@router.get("/users/self", response_model=Union[StudentSchema, InstructorSchema])
async def get_own_user(
    *,
    request: Request,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(RequireLoginPermission))
):
    onyen = request.user.onyen
    user = await UserService(db).get_user_by_onyen(onyen)
    return user

@router.get("/users/{pid:str}/ldap", response_model=LDAPUserInfoSchema)
async def get_ldap_user(
    *,
    request: Request,
    perm: None = Depends(PermissionDependency(UserIsSuperuserPermission)),
    pid: str
):
    return LDAPService().get_user_info(pid)