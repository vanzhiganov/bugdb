from hashlib import sha256
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, CHAR, Text, DateTime
from BugDB.db import database


class UsersModel(database.Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True)
    password = Column(String(256))
    username = Column(String(64))
    # A - Active, I - Inactive
    status = Column(String(1), default="A")

    def __init__(self, email, password, username, status="A"):
        self.email = email
        self.password = password
        self.username = username
        self.status = status

    def __repr__(self):
        return "<user id={} email={} username={} status={}>".format(
            self.id, self.email, self.username, self.status
        )

    @staticmethod
    def get_hash(string: str) -> str:
        return sha256(string.encode()).hexdigest()

    @classmethod
    def login(cls, email, password):
        password_hash = cls.get_hash(password)
        user = database.session.query(cls).filter_by(
            email=email, password=password_hash
        ).first()
        print(user)
        return user

    @classmethod
    def is_exists_email(cls, email):
        cnt = database.session.query(cls).filter_by(email=email).count()
        if cnt == 0:
            return False
        return True

    @classmethod
    def get_email_by_id(cls, user_id: int) -> str:
        return database.session.query(cls.email).filter_by(id=user_id).scalar()


# class ProjectsModel():
#     __tablename__ = "projects"
#
#     id = Column(Integer, primary_key=True)
#     user_id = Column(ForeignKey(UsersModel.id))
#     name = Column(String(64), nullable=False)
#     description = Column(String(256))
#     # public, private
#     access = Column(String(12), default="private")


class MDebugModel():
    __tablename__ = "m_debug"
    text = Column(Text)


class BugHeaderModel(database.Model):
    __tablename__ = "bug_header"
    id = Column(Integer, primary_key=True)
    title = Column(String(254), nullable=False)
    description = Column(Text)
    assigned_to_user_id = Column(ForeignKey(UsersModel.id))
    customer = Column(String(10))
    status = Column(String(10))
    priority = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)


class BugBodyModel(database.Model):
    __tablename__ = "bug_body"
    id = Column(Integer, primary_key=True)
    bug_id = Column(ForeignKey(BugHeaderModel.id))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    bug_update = Column(Text)
    updated_by = Column(ForeignKey(UsersModel.id))


class StatusesModel(database.Model):
    __tablename__ = "statuses"
    id = Column(Integer, primary_key=True)
    status = Column(String(256))
    description = Column(Text)


class CategoriesModel(database.Model):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    description = Column(String(256))
    parent_id = Column(Integer)
    owner_id = Column(ForeignKey(UsersModel.id), nullable=True)

    def __init__(self, name, description, parent_id, owner_id):
        self.name = name
        self.description = description
        self.parent_id = parent_id
        self.owner_id = owner_id

    @classmethod
    def get_all(cls):
        return database.session.query(cls).all()
