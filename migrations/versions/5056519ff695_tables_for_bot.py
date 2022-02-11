"""tables for bot

Revision ID: 5056519ff695
Revises: 91d0ea1450ac
Create Date: 2022-02-11 15:58:18.096886

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5056519ff695'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('RatingQuery',
    sa.Column('message_id', sa.Integer(), nullable=False),
    sa.Column('image_uuid', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('message_id')
    )
    op.create_index(op.f('ix_RatingQuery_message_id'), 'RatingQuery', ['message_id'], unique=False)
    op.create_table('tg_users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tg_user_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('tg_user_name', sa.String(length=255), nullable=True),
    sa.Column('first_name', sa.String(length=255), nullable=True),
    sa.Column('last_name', sa.String(length=255), nullable=True),
    sa.Column('lang', sa.String(length=4), nullable=True),
    sa.Column('tags_format', postgresql.ENUM('instagram', 'list_tags', name='tagformat', 
                                             create_type=True), nullable=True),
    sa.Column('rating', sa.Boolean(), nullable=True),
    sa.Column('free_act', sa.Integer(), nullable=True),
    sa.Column('create_at', sa.DateTime(), nullable=True),
    sa.Column('bot_feedback', sa.String(length=10000), nullable=True),
    sa.Column('is_banned', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tg_users_tg_user_id'), 'tg_users', ['tg_user_id'], unique=True)
    op.create_index(op.f('ix_tg_users_user_id'), 'tg_users', ['user_id'], unique=False)
    op.create_table('tg_actions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tg_user_id', sa.Integer(), nullable=True),
    sa.Column('action_type', postgresql.ENUM('desc_tags', 'desc', 'tags',
                                             name='action', create_type=True), nullable=True),
    sa.Column('image_uuid', sa.String(length=50), nullable=True),
    sa.Column('image_name', sa.String(), nullable=True),
    sa.Column('lang', sa.String(length=4), nullable=True),
    sa.Column('image_type', sa.String(), nullable=True),
    sa.Column('image_size', sa.Integer(), nullable=True),
    sa.Column('create_at', sa.DateTime(), nullable=True),
    sa.Column('responce', sa.String(length=20000), nullable=True),
    sa.ForeignKeyConstraint(['tg_user_id'], ['tg_users.tg_user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tg_actions_image_uuid'), 'tg_actions', ['image_uuid'], unique=False)
    op.create_table('tg_chat_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tg_msg_id', sa.Integer(), nullable=True),
    sa.Column('tg_user_id', sa.Integer(), nullable=True),
    sa.Column('user_msg', sa.String(length=10000), nullable=True),
    sa.Column('bot_msg', sa.String(length=10000), nullable=True),
    sa.Column('bot_message_edit', sa.Boolean(), nullable=True),
    sa.Column('create_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['tg_user_id'], ['tg_users.tg_user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tg_chat_history')
    op.drop_index(op.f('ix_tg_actions_image_uuid'), table_name='tg_actions')
    op.drop_table('tg_actions')
    op.drop_index(op.f('ix_tg_users_user_id'), table_name='tg_users')
    op.drop_index(op.f('ix_tg_users_tg_user_id'), table_name='tg_users')
    op.drop_table('tg_users')
    op.drop_index(op.f('ix_RatingQuery_message_id'), table_name='RatingQuery')
    op.drop_table('RatingQuery')
    # ### end Alembic commands ###