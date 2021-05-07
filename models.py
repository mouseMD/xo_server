from sqlalchemy.orm import declarative_base
from sqlalchemy import Integer, String, Boolean, Column
from utils import current_timestamp

Base = declarative_base()


class UserException(Exception):
    pass


class User(Base):
    """The User model."""
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True),
    created_at = Column(Integer, default=current_timestamp),
    last_seen_at = Column(Integer, default=current_timestamp, onupdate=current_timestamp),
    login = Column(String(32), nullable=False, unique=True),
    password_hash = Column(String(256), nullable=False),
    online = Column(Boolean, default=True),
    deleted = Column(Boolean, default=False)

    __mapper_args__ = {"eager_defaults": True}

    @staticmethod
    def create_new(login: str, password: str):
        raise UserException(f'User {login} already exists!')
