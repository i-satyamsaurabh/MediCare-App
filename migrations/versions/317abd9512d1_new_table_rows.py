"""New table rows

Revision ID: 317abd9512d1
Revises: d44211196016
Create Date: 2025-01-11 12:19:09.756857

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '317abd9512d1'
down_revision = 'd44211196016'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointment', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'patient', ['patient_id'], ['user_id'])

    with op.batch_alter_table('prescription', schema=None) as batch_op:
        batch_op.add_column(sa.Column('dosage', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('frequency', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('duration', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('prescription', schema=None) as batch_op:
        batch_op.drop_column('duration')
        batch_op.drop_column('frequency')
        batch_op.drop_column('dosage')

    with op.batch_alter_table('appointment', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'patient', ['patient_id'], ['id'])

    # ### end Alembic commands ###
