from datetime import datetime
import uuid
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.dialects.postgresql import UUID
from typing_extensions import List
from db.session import Base


class User(Base):
	__tablename__ = "users"
	
	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		primary_key=True,
		default= uuid.uuid4,
		index=True
	)
	name: Mapped[str] = mapped_column(String)
	email: Mapped[str] = mapped_column(String, index = True)
	hashed_password: Mapped[str] = mapped_column(String, nullable=False)
	bio: Mapped[str] = mapped_column(String, default="")
	avatar_url: Mapped[str] = mapped_column(String, default="")
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone = True),
		server_default=func.now(),
		nullable=False
	)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default=func.now(),
		onupdate=func.now(),
		nullable=False
	)
	expense: Mapped[List["Expense"]] = relationship(back_populates="user")
	
	refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
    	back_populates="user",
     	cascade="all, delete-orphan"
	)