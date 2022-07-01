"""Add internal flag column to module_version table and foreign key to module provider to point to latest version

Revision ID: ef71db86c2a1
Revises: b0f952e4a027
Create Date: 2022-06-01 06:50:03.299444

"""
from distutils.version import LooseVersion
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ef71db86c2a1'
down_revision = 'b0f952e4a027'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('module_provider', sa.Column('latest_version_id', sa.Integer(), nullable=True))
    with op.batch_alter_table('module_provider', schema=None) as batch_op:
        batch_op.create_foreign_key('latest_version_id', 'module_version', ['latest_version_id'], ['id'], onupdate='CASCADE', ondelete='SET NULL', use_alter=True)

    # Iterate through all module providers, updating latest version ID
    c = op.get_bind()
    res = c.execute("""
        SELECT
            module_version.id AS module_version_id,
            module_version.version as version,
            module_provider.id AS module_provider_id
        FROM module_version
        INNER JOIN module_provider ON module_provider.id=module_version.module_provider_id
        WHERE module_version.beta=0 AND module_version.published=1
    """)
    latest_versions = {}
    for row in res:
        version = row[1]
        provider_id = row[2]

        # Check if module provider is in latest version map and add
        if provider_id not in latest_versions:
            latest_versions[provider_id] = row

        # Check if current version is higher than the current seen highest
        elif LooseVersion(version) > LooseVersion(latest_versions[provider_id][1]):
            latest_versions[provider_id] = row

    # Iterate through all the module providers and update the latest_version_id column
    for module_provider_id in latest_versions:
        c.execute(
            sa.sql.text(
                """
                UPDATE module_provider
                SET latest_version_id=:latest_version_id
                WHERE id=:module_provider_id
                """
            ),
            latest_version_id=latest_versions[module_provider_id][0],
            module_provider_id=module_provider_id
        )

    # Add internal column, allowing nullable value
    op.add_column('module_version', sa.Column('internal', sa.BOOLEAN(), nullable=True))

    # Set any pre-existing rows to internal false
    op.execute("""UPDATE module_version set internal=0""")

    # Disable nullable flag in column
    with op.batch_alter_table('module_version', schema=None) as batch_op:
        batch_op.alter_column('internal', existing_type=sa.BOOLEAN(), nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('module_version', 'internal')
    op.drop_constraint(None, 'module_provider', type_='foreignkey')
    op.drop_column('module_provider', 'latest_version_id')
    # ### end Alembic commands ###
