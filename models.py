from sqlalchemy.orm import declarative_base
from sqlalchemy import Integer, String, Boolean, Column, ForeignKey, JSON, select
from utils import current_timestamp
from passlib.hash import sha256_crypt

Base = declarative_base()


class UserException(Exception):
    pass


class User(Base):
    """The User model."""
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(Integer, default=current_timestamp)
    last_seen_at = Column(Integer, default=current_timestamp, onupdate=current_timestamp)
    login = Column(String(32), nullable=False, unique=True)
    password_hash = Column(String(256), nullable=False)
    online = Column(Boolean, default=True)
    deleted = Column(Boolean, default=False)

    __mapper_args__ = {"eager_defaults": True}

    @staticmethod
    def create_new(login: str, password: str):
        user = User()
        user.login = login
        user.password_hash = sha256_crypt.hash(password)
        return user

    def check_password(self, password: str):
        return sha256_crypt.verify(password, self.password_hash)

    def ping(self):
        self.last_seen_at = current_timestamp()
        self.online = True

    @staticmethod
    async def find_offline_users(session):
        stmt = select(User).where(User.last_seen_at < current_timestamp() - 60, User.online == True)
        async with session.begin():
            result = await session.execute(stmt)
            users = result.scalars().all()
            for user in users:
                user.online = False
                session.add(user)


class EntryException(Exception):
    pass


class Entry(Base):
    """The Entry model."""
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(Integer, default=current_timestamp)
    user_id = Column(Integer, ForeignKey('users.id'))
    active = Column(Boolean, default=True)
    criteria = Column(JSON)

    __mapper_args__ = {"eager_defaults": True}
