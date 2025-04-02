"""Rename user table since user is a reserved keyword in postgres

Revision ID: 0babbb4e741d
Revises: b6ec775bea28
Create Date: 2023-08-10 23:27:12.162536+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0babbb4e741d'
down_revision = 'b6ec775bea28'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table('user', 'user_account')
    op.execute("ALTER SEQUENCE user_id_seq RENAME TO user_account_id_seq")
    op.drop_constraint('student_id_fkey', 'student', type_='foreignkey')
    op.create_foreign_key('student_id_fkey', 'student', 'user_account', ['id'], ['id'])
    


def downgrade() -> None:
    op.rename_table('user_account', 'user')
    op.execute("ALTER SEQUENCE user_account_id_seq RENAME TO user_id_seq")
    op.drop_constraint('student_id_fkey', 'student', type_='foreignkey')
    op.create_foreign_key('student_id_fkey', 'student', 'user', ['id'], ['id'])