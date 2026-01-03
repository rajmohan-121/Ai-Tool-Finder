from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.database import Base


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)


class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    use_case = Column(String, nullable=False)
    category = Column(String, nullable=False)
    pricing = Column(String, nullable=False)
    avg_rating = Column(Float, default=0.0)


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    tool_id = Column(Integer, ForeignKey("tools.id"))
    rating = Column(Integer)
    comment = Column(String)
    status = Column(String, default="Pending")
