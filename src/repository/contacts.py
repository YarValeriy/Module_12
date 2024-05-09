from fastapi import Depends
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import Contact, User
from src.schemas import ContactCreate, ContactUpdate
from datetime import date
from sqlalchemy import extract, and_


async def create_contact(contact: ContactCreate, user: User, db: Session = Depends(get_db)):
    """
    Creates a new contact for a specific user.

    :param contact: The data for the contact to create.
    :type contact: ContactModel
    :param user: The user to create the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The newly created contact.
    :rtype: Contact

    """
    db_contact = Contact(**contact.dict())
    db_contact.users.append(user)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


async def get_contact(contact_id: int, user: User, db: Session):
    """
    Retrieves a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param user: The user to retrieve the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The contact with the specified ID, or None if it does not exist.
    :rtype: Contact | None

    """
    return db.query(Contact).filter(
        and_(Contact.id == contact_id, Contact.users.any(id=user.id))
    ).first()


# Update a contact per ID in the database
async def update_contact(contact_id: int, contact_update: ContactUpdate, user: User, db: Session):
    """
    Updates a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param contact_update: The updated data for the contact.
    :type contact_update: ContactUpdate
    :param user: The user to update the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The updated contact, or None if it does not exist.
    :rtype: Contact | None

    """
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
    """
    Removes a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to remove.
    :type contact_id: int
    :param user: The user to remove the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The removed contact, or None if it does not exist.
    :rtype: Contact | None

    """
    db_contact = await get_contact(contact_id, user, db)
    if not db_contact:
        return None
    db.delete(db_contact)
    db.commit()
    return {"message": "Contact deleted successfully"}


async def get_birthdays(start_date: date, end_date: date, user: User, db: Session):
    """
    Retrieves a list of contacts for a specific user, whose birthday will be in the next 7 days.

    :param start_date: The first day the search period.
    :type start_date: date
    :param end_date: The last day of the search period.
    :type end_date: date
    :param user: The user to retrieve contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts.
    :rtype: List[Contact]

    """
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

    return birthdays.all()


# Search for contacts by name, surname, email or phone
async def get_contacts(
        name, surname, email, phone, birthday, user: User, db
):
    """
    Retrieves a list of contacts for a specific user.

    :param name: The name of the contact to retrieve.
    :type name: str
    :param surname: The surname of the contact to retrieve.
    :type surname: str
    :param email: The email of the contact to retrieve.
    :type email: str
    :param phone: The phone of the contact to retrieve.
    :type phone: str
    :param birthday: The birthday of the contact to retrieve.
    :type birthday: date
    :param user: The user to retrieve contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts.
    :rtype: List[Contact]

    """
    query = db.query(Contact).filter(Contact.users.any(id=user.id))
    filter_conditions = []

    if name:
        filter_conditions.append(Contact.name == name)
    if surname:
        filter_conditions.append(Contact.surname == surname)
    if email:
        filter_conditions.append(Contact.email == email)
    if phone:
        filter_conditions.append(Contact.phone == phone)
    if birthday:
        filter_conditions.append(Contact.birthday == birthday)

    if filter_conditions:
        query = query.filter(and_(*filter_conditions))

    return query.all()
