import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    column_id: Mapped[str] = mapped_column(String, ForeignKey("columns.id"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1000)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cover_color: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    column: Mapped["Column"] = relationship(back_populates="cards")
    assignees: Mapped[list["CardAssignee"]] = relationship(back_populates="card", cascade="all, delete-orphan")
    labels: Mapped[list["CardLabel"]] = relationship(back_populates="card", cascade="all, delete-orphan")
    comments: Mapped[list["Comment"]] = relationship(back_populates="card", cascade="all, delete-orphan", order_by="Comment.created_at")


class CardAssignee(Base):
    __tablename__ = "card_assignees"

    card_id: Mapped[str] = mapped_column(String, ForeignKey("cards.id"), primary_key=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), primary_key=True)

    card: Mapped["Card"] = relationship(back_populates="assignees")
    user: Mapped["User"] = relationship()


class CardLabel(Base):
    __tablename__ = "card_labels"

    card_id: Mapped[str] = mapped_column(String, ForeignKey("cards.id"), primary_key=True)
    label_id: Mapped[str] = mapped_column(String, ForeignKey("labels.id"), primary_key=True)

    card: Mapped["Card"] = relationship(back_populates="labels")
    label: Mapped["Label"] = relationship()
