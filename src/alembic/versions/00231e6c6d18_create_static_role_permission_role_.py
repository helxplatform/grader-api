"""Create static role/permission/role-permission-bindings resources in database automatically.

Revision ID: 00231e6c6d18
Revises: 27622169eb7d
Create Date: 2023-08-24 15:56:32.394979+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '00231e6c6d18'
down_revision = '27622169eb7d'
branch_labels = None
depends_on = None


# Get, create, delete, modify
permissions = [
    {"name": "assignment:get"},
    {"name": "assignment:create"},
    {"name": "assignment:modify"},
    {"name": "assignment:delete"},

    {"name": "course:get"},
    {"name": "course:create"},
    {"name": "course:modify"},
    {"name": "course:delete"},

    {"name": "student:get"},
    {"name": "student:create"},
    {"name": "student:modify"},
    {"name": "student:delete"},

    {"name": "instructor:get"},
    {"name": "instructor:create"},
    {"name": "instructor:modify"},
    {"name": "instructor:delete"},
    
    {"name": "submission:get"},
    {"name": "submission:create"},
    {"name": "submission:modify"},
    {"name": "submission:delete"},
]

roles = [
    {"name": "student"},
    {"name": "instructor"},
    # Note: admin role does not require role permission bindings, functionality is baked directly into the permission handler.
    {"name": "admin"}
]

# Note that access to owned resources is an implied permission, e.g. students do not need the submission:get permission
# to list their own submissions, since they own these resources. "submission:get" indicates that a user is authorized
# to list any user's submissions.
role_permissions = [
   {"role_name": "student", "permission_name": "course:get"},
   {"role_name": "student", "permission_name": "submission:create"},
   {"role_name": "student", "permission_name": "instructor:get"},

   {"role_name": "instructor", "permission_name": "assignment:get"},
   {"role_name": "instructor", "permission_name": "assignment:create"},
   {"role_name": "instructor", "permission_name": "assignment:modify"},
   {"role_name": "instructor", "permission_name": "assignment:delete"},
   {"role_name": "instructor", "permission_name": "course:get"},
   {"role_name": "instructor", "permission_name": "course:create"},
   {"role_name": "instructor", "permission_name": "course:modify"},
   {"role_name": "instructor", "permission_name": "student:get"},
   {"role_name": "instructor", "permission_name": "student:create"},
   {"role_name": "instructor", "permission_name": "student:modify"},
   {"role_name": "instructor", "permission_name": "instructor:get"},
   {"role_name": "instructor", "permission_name": "submission:get"}
]

def upgrade() -> None:
    meta = sa.MetaData()
    meta.reflect(
        bind=op.get_bind(),
        only=("user_permission", "user_role", "user_role_permission")
    )
    user_permission_table = sa.Table("user_permission", meta)
    user_role_table = sa.Table("user_role", meta)
    user_role_permission_table = sa.Table("user_role_permission", meta)
    op.bulk_insert(
        user_permission_table,
        permissions
    )
    op.bulk_insert(
        user_role_table,
        roles
    )
    op.bulk_insert(
        user_role_permission_table,
        role_permissions
    )
    


def downgrade() -> None:
    conn = op.get_bind()
    for role_permission in role_permissions:
        conn.execute(
            sa.text("DELETE FROM user_role_permission WHERE role_name=:role_name AND permission_name=:permission_name"),
            parameters=role_permission
        )
    conn.execute(
        sa.text("DELETE FROM user_role WHERE name IN :roles"),
        parameters={"roles": tuple([role["name"] for role in roles])}
    )
    conn.execute(
        sa.text("DELETE FROM user_permission WHERE name IN :permissions"),
        parameters={"permissions": tuple([permission["name"] for permission in permissions])}
    )