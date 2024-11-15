from sqlalchemy.orm import Mapped, mapped_column


class IntegerIdMixin:
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
