"""Create table for neural net and gbm persistence

Revision ID: 9599db59caaa
Revises: 
Create Date: 2021-06-23 15:22:05.295203

"""
from alembic import op
import sqlalchemy as sa
# For JSONB datatype
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '9599db59caaa'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "gradient_boosting_model_predictions",
        sa.Column("id", sa.Integer(), nullable=False,primary_key=True),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column(
            "datetime_captured",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("model_version", sa.String(length=36), nullable=False),
        sa.Column("inputs", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("outputs", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_gradient_boosting_model_predictions_datetime_captured"),
        "gradient_boosting_model_predictions",
        ["datetime_captured"],
        unique=False,
    )
    op.create_table(
        "neural_net_model_predictions",
        sa.Column("id", sa.Integer(), nullable=False,primary_key=True),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column(
            "datetime_captured",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("model_version", sa.String(length=36), nullable=False),
        sa.Column("inputs", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("outputs", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_neural_net_model_predictions_datetime_captured"),
        "neural_net_model_predictions",
        ["datetime_captured"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f("ix_neural_net_model_predictions_datetime_captured"),
        table_name="neural_net_model_predictions",
    )
    op.drop_table("neural_net_model_predictions")
    op.drop_index(
        op.f("ix_gradient_boosting_model_predictions_datetime_captured"),
        table_name="gradient_boosting_model_predictions",
    )
    op.drop_table("gradient_boosting_model_predictions")
