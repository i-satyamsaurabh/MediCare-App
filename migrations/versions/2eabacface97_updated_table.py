"""Updated  table

Revision ID: 2eabacface97
Revises: 563c80bcc032
Create Date: 2025-01-09 00:37:19.849581

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2eabacface97'
down_revision = '563c80bcc032'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('notification',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('doctor_id', sa.Integer(), nullable=False),
    sa.Column('message', sa.String(length=255), nullable=False),
    sa.Column('is_read', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['doctor_id'], ['doctor.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('notifications')
    with op.batch_alter_table('appointment', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'patient', ['patient_id'], ['user_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointment', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'patient', ['patient_id'], ['id'])

    op.create_table('notifications',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('doctor_id', sa.INTEGER(), nullable=False),
    sa.Column('message', sa.VARCHAR(length=255), nullable=False),
    sa.Column('appointment_time', sa.DATETIME(), nullable=False),
    sa.Column('timestamp', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['doctor_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('notification')
    # ### end Alembic commands ###
