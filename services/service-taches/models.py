from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Todo(Base):
    __tablename__ = "todos"

    id          = Column(Integer, primary_key=True, index=True)
    titre       = Column(String, nullable=False)
    description = Column(String, nullable=True)
    termine     = Column(Boolean, default=False)
