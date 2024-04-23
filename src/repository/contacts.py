from fastapi import Depends
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import Contact, User
from src.schemas import ContactCreate, ContactUpdate
from datetime import date, timedelta
from sqlalchemy import extract, or_, and_, func


# Create a new contact in the database
async def create_contact(contact: ContactCreate, user: User, db: Session = Depends(get_db)):
    db_contact = Contact(**contact.dict())
    db_contact.users.append(user)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


async def get_contact(contact_id: int, user: User, db: Session):
    return db.query(Contact).filter(
        and_(Contact.id == contact_id, Contact.users.any(id=user.id))
    ).first()


# Update a contact per ID in the database
async def update_contact(contact_id: int, contact_update: ContactUpdate, user: User, db: Session):
    db_contact = await get_contact(contact_id, user, db)
    if not db_contact:
        return None
    for field, value in contact_update.dict(exclude_unset=True).items():
        setattr(db_contact, field, value)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


async def delete_contact(contact_id: int, user: User, db: Session):
    db_contact = await get_contact(contact_id, user, db)
    if not db_contact:
        return None
    db.delete(db_contact)
    db.commit()
    return {"message": "Contact deleted successfully"}


async def get_birthdays(start_date: date, end_date: date, user: User, db: Session):
    month = extract('month', Contact.birthday)
    day = extract('day', Contact.birthday)

    birthdays = db.query(Contact).filter(Contact.users.any(id=user.id))
    if end_date.day > start_date.day: # sample period is within the current month
        birthdays = birthdays.filter(
            (month == start_date.month) &
            (day >= start_date.day) &
            (day <= end_date.day))
    else:
        birthdays = birthdays.filter(
            ((month == start_date.month) & (day >= start_date.day)) |
            ((month == end_date.month) & (day <= end_date.day))
        )

    return birthdays


# Search for contacts by name, surname, email or phone
async def get_contacts(
        name, surname, email, phone, birthday, user: User, db
):
    query = db.query(Contact).filter(Contact.users.any(id=user.id))
    if name:
        query = query.filter(Contact.name == name)
    if surname:
        query = query.filter(Contact.surname == surname)
    if email:
        query = query.filter(Contact.email == email)
    if phone:
        query = query.filter(Contact.phone == phone)
    if birthday:
        query = query.filter(Contact.birthday == birthday)
    return query.all()
