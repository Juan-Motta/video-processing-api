from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.base import Base
from src.core.database.mixins.active import IsActiveMixin
from src.core.database.mixins.id import IntegerIdMixin
from src.core.database.mixins.timestamp import TimestampMixin

if TYPE_CHECKING:
    from src.apps.tasks.models import Task
    from src.apps.users.models import User


class Video(IntegerIdMixin, TimestampMixin, IsActiveMixin, Base):
    __tablename__ = "videos"
    title: Mapped[str]
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="videos")
    tasks_as_original: Mapped[list["Task"]] = relationship(
        "Task", foreign_keys="[Task.original_video_id]", back_populates="original_video"
    )
    tasks_as_processed: Mapped[list["Task"]] = relationship(
        "Task",
        foreign_keys="[Task.processed_video_id]",
        back_populates="processed_video",
    )
    filename: Mapped[str]
    url: Mapped[str]
    score: Mapped[Optional[float]]
