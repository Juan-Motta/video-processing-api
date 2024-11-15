"""12_10_2024

Revision ID: 85f38347a14f
Revises: c6a8c25ddd1d
Create Date: 2024-10-12 17:09:14.725450

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "85f38347a14f"
down_revision: Union[str, None] = "c6a8c25ddd1d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO users (username, email, password, is_active)
        VALUES
        ('jhon', 'jhondoe@example.com', 'pbkdf2_sha256$260000$YD0xbHumAP9wqeV3wGp2LA==$3QYuTI4y4u9d6irw+MqOjO6Ns67VLrHaP6m/5e2n+Ng=', true),
        ('pepito', 'pepito@example.com', 'pbkdf2_sha256$260000$YD0xbHumAP9wqeV3wGp2LA==$3QYuTI4y4u9d6irw+MqOjO6Ns67VLrHaP6m/5e2n+Ng=', true),
        ('juanito', 'juanito@example.com', 'pbkdf2_sha256$260000$YD0xbHumAP9wqeV3wGp2LA==$3QYuTI4y4u9d6irw+MqOjO6Ns67VLrHaP6m/5e2n+Ng=', true),
        ('maria', 'maria@example.com', 'pbkdf2_sha256$260000$YD0xbHumAP9wqeV3wGp2LA==$3QYuTI4y4u9d6irw+MqOjO6Ns67VLrHaP6m/5e2n+Ng=', true);
    """
    )


def downgrade() -> None:
    pass
