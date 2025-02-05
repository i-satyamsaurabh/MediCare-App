"""New table row

Revision ID: d44211196016
Revises: 771a11f9fe2b
Create Date: 2025-01-10 23:27:44.550454

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd44211196016'
down_revision = '771a11f9fe2b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('prescription_id', sa.Integer(), nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'patient', ['patient_id'], ['user_id'])
        batch_op.create_foreign_key(None, 'prescription', ['prescription_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointment', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'patient', ['patient_id'], ['id'])
        batch_op.drop_column('prescription_id')

    # ### end Alembic commands ###
