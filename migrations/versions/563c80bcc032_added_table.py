"""Added  table

Revision ID: 563c80bcc032
Revises: 6e551e55bcfe
Create Date: 2025-01-09 00:20:44.793438

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '563c80bcc032'
down_revision = '6e551e55bcfe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('notifications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('doctor_id', sa.Integer(), nullable=False),
    sa.Column('message', sa.String(length=255), nullable=False),
    sa.Column('appointment_time', sa.DateTime(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['doctor_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('message')
    with op.batch_alter_table('appointment', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'patient', ['patient_id'], ['user_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointment', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'patient', ['patient_id'], ['id'])

    op.create_table('message',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('sender_id', sa.INTEGER(), nullable=False),
    sa.Column('receiver_id', sa.INTEGER(), nullable=False),
    sa.Column('content', sa.TEXT(), nullable=False),
    sa.Column('timestamp', sa.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('notifications')
    # ### end Alembic commands ###
