"""add-resource-presets

Revision ID: 8e660aa31fe3
Revises: 01456c812164
Create Date: 2019-03-30 01:45:07.525096

"""
from decimal import Decimal

import sqlalchemy as sa
from alembic import op

from ai.backend.common.types import BinarySize, ResourceSlot
from ai.backend.manager.models import keypair_resource_policies
from ai.backend.manager.models.base import ResourceSlotColumn

# revision identifiers, used by Alembic.
revision = "8e660aa31fe3"
down_revision = "01456c812164"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "resource_presets",
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("resource_slots", ResourceSlotColumn(), nullable=False),
        sa.PrimaryKeyConstraint("name", name=op.f("pk_resource_presets")),
    )
    # Add initial fixtures for resource presets
    query = """
    INSERT INTO resource_presets
    VALUES (
        'small',
        '{"cpu":"1","mem":"2147483648"}'::jsonb
    );
    INSERT INTO resource_presets
    VALUES (
        'small-gpu',
        '{"cpu":"1","mem":"2147483648","cuda.device":"1","cuda.shares":"0.5"}'::jsonb
    );
    INSERT INTO resource_presets
    VALUES (
        'medium',
        '{"cpu":"2","mem":"4294967296"}'::jsonb
    );
    INSERT INTO resource_presets
    VALUES (
        'medium-gpu',
        '{"cpu":"2","mem":"4294967296","cuda.device":"1","cuda.shares":"1.0"}'::jsonb
    );
    INSERT INTO resource_presets
    VALUES (
        'large',
        '{"cpu":"4","mem":"8589934592"}'::jsonb
    );
    INSERT INTO resource_presets
    VALUES (
        'large-gpu',
        '{"cpu":"4","mem":"8589934592","cuda.device":"2","cuda.shares":"2.0"}'::jsonb
    );
    """
    connection = op.get_bind()
    connection.execute(query)

    query = """
    SELECT name, total_resource_slots
    FROM keypair_resource_policies
    """
    connection = op.get_bind()
    result = connection.execute(query)
    updates = []
    for row in result:
        converted = ResourceSlot(row["total_resource_slots"])
        if "mem" in converted:
            converted["mem"] = Decimal(BinarySize.from_str(converted["mem"]))
            updates.append(
                (
                    row["name"],
                    converted,
                )
            )
    for name, slots in updates:
        query = (
            sa.update(keypair_resource_policies)
            .values(total_resource_slots=slots)
            .where(keypair_resource_policies.c.name == name)
        )
        connection.execute(query)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("resource_presets")
    # ### end Alembic commands ###
