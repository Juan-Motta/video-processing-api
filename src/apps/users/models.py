from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.base import Base
from src.core.database.mixins.active import IsActiveMixin
from src.core.database.mixins.id import IntegerIdMixin
from src.core.database.mixins.timestamp import TimestampMixin

if TYPE_CHECKING:
    from src.apps.tasks.models import Task
    from src.apps.videos.models import Video


class User(IntegerIdMixin, TimestampMixin, IsActiveMixin, Base):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]

    videos: Mapped[List["Video"]] = relationship("Video", back_populates="user")
    tasks: Mapped[List["Task"]] = relationship(back_populates="user")
