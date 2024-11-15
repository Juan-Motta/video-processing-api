from sqlalchemy.orm import Mapped, mapped_column


class IsActiveMixin:
    is_active: Mapped[bool] = mapped_column(default=True)
