import uuid
from datetime import datetime
from db.enums import CategoryEnum, ExpenseTypeEnum
from db.session import Base
from sqlalchemy import DateTime, ForeignKey, Float, String, func, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
    	UUID(as_uuid=True),
    	ForeignKey("users.id", ondelete="CASCADE"),
    	nullable=False
    )
    title: Mapped[str] = mapped_column(String, index=True)
    desc: Mapped[str] = mapped_column(String)
    amount: Mapped[float] = mapped_column(Float, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    category: Mapped[CategoryEnum] = mapped_column(SAEnum(CategoryEnum), default=CategoryEnum.others)
    type: Mapped[ExpenseTypeEnum] = mapped_column(SAEnum(ExpenseTypeEnum), default=ExpenseTypeEnum.debited)
    user: Mapped["User"] = relationship(back_populates="expense")