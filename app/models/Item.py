from sqlalchemy import Column, Integer, String,Text, Numeric
from app.connection.database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)  # ✅ Text
    price = Column(Numeric(10, 2), nullable=True)
