from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.base import Base
from src.core.database.mixins.active import IsActiveMixin
from src.core.database.mixins.id import IntegerIdMixin
from src.core.database.mixins.timestamp import TimestampMixin

if TYPE_CHECKING:
    from src.apps.users.models import User
    from src.apps.videos.models import Video


class TaskStatusEnum(Enum):
    PENDING = "pending"
    UPLOADED = "uploaded"
    PROCESSED = "processed"
    FAILURE = "failure"


class Task(IntegerIdMixin, TimestampMixin, IsActiveMixin, Base):
    __tablename__ = "tasks"
    task_id: Mapped[Optional[str]]
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="tasks")
    original_video_id: Mapped[Optional[int]] = mapped_column(sa.ForeignKey("videos.id"))
    original_video: Mapped["Video"] = relationship(
        "Video", foreign_keys=[original_video_id], back_populates="tasks_as_original"
    )
    processed_video_id: Mapped[Optional[int]] = mapped_column(
        sa.ForeignKey("videos.id")
    )
    processed_video: Mapped["Video"] = relationship(
        "Video", foreign_keys=[processed_video_id], back_populates="tasks_as_processed"
    )
    status: Mapped[TaskStatusEnum] = mapped_column(
        sa.Enum(
            TaskStatusEnum,
            native_enum=False,
            validate_strings=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        default=TaskStatusEnum.PENDING,
    )
