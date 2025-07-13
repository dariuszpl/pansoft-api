from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    allegro_id = Column(String, unique=True, index=True)
    access_token = Column(String)
    refresh_token = Column(String)
    expires_in = Column(Integer)