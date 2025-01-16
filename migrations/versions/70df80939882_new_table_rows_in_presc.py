"""New table rows IN PRESC

Revision ID: 70df80939882
Revises: 600911d1114a
Create Date: 2025-01-11 13:39:34.443828

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70df80939882'
down_revision = '600911d1114a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('prescription',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('appointment_id', sa.Integer(), nullable=False),
    sa.Column('diagnosis', sa.String(length=200), nullable=False),
    sa.Column('medicines', sa.Text(), nullable=False),
    sa.Column('dosage', sa.Text(), nullable=True),
    sa.Column('frequency', sa.Text(), nullable=True),
    sa.Column('duration', sa.Text(), nullable=True),
    sa.Column('instructions', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['appointment_id'], ['appointment.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('appointment', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'patient', ['patient_id'], ['user_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointment', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'patient', ['patient_id'], ['id'])

    op.drop_table('prescription')
    # ### end Alembic commands ###
