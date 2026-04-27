from sqlalchemy import CheckConstraint
from sqlalchemy.types import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False, server_default='')
    price: Mapped[int] = mapped_column(CheckConstraint('price > 0'), nullable=False)
    count: Mapped[int] = mapped_column(CheckConstraint('count > 0'), nullable=False)