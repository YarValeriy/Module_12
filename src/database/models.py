from sqlalchemy import Column, Integer, String, func, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey, Table
from sqlalchemy.sql.sqltypes import DateTime, Boolean

Base = declarative_base()
user_m2m_contact = Table(
    "user_m2m_contact",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
    Column("contact_id", Integer, ForeignKey("contacts.id", ondelete="CASCADE")),
)


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    surname = Column(String, index=True)
    email = Column(String)
    phone = Column(String)
    birthday = Column(Date)
    additional_data = Column(String, nullable=True)
    created_at = Column('created_at', DateTime, default=func.now())
    users = relationship("User", secondary=user_m2m_contact, back_populates="contacts")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(250), nullable=False, unique=True)
    confirmed = Column(Boolean, default=False)
    password = Column(String(255), nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    contacts = relationship("Contact", secondary=user_m2m_contact, back_populates="users")
