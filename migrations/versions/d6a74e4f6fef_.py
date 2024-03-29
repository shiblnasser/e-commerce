"""empty message

Revision ID: d6a74e4f6fef
Revises: 5fed4b986642
Create Date: 2024-02-08 15:16:03.853591

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd6a74e4f6fef'
down_revision = '5fed4b986642'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.String(length=50), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(length=50), nullable=False),
    sa.Column('user_type', sa.String(length=50), nullable=False),
    sa.Column('status', sa.String(length=10), nullable=False),
    sa.Column('address', sa.String(length=50), nullable=False),
    sa.Column('created_on', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_on', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('product',
    sa.Column('id', sa.String(length=50), nullable=False),
    sa.Column('user_id', sa.String(length=50), nullable=True),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('status', sa.String(length=10), nullable=False),
    sa.Column('description', sa.String(length=50), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('created_on', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_on', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('orders',
    sa.Column('id', sa.String(length=50), nullable=False),
    sa.Column('user_id', sa.String(length=50), nullable=True),
    sa.Column('product_id', sa.String(length=50), nullable=True),
    sa.Column('status', sa.String(length=10), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('created_on', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_on', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('orders')
    op.drop_table('product')
    op.drop_table('user')
    # ### end Alembic commands ###
