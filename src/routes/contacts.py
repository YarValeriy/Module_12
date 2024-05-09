"""
Module for contact routes.
The `router` instance is created with a prefix of '/contacts' and tagged as "contacts".
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import User
from src.schemas import ContactCreate, ContactResponse, ContactUpdate
from src.repository import contacts as repository_contacts
from datetime import datetime, timedelta, date
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=["contacts"])


# @router.get("/birthdays", response_model=List[ContactResponse], description='No more than 10 requests per minute',
#             dependencies=[Depends(RateLimiter(times=10, seconds=60))])
@router.get("/birthdays", response_model=List[ContactResponse])
async def get_birthdays(db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Route handler for retrieving upcoming birthdays.
    This function handles GET requests to '/contacts/birthdays' for retrieving contacts with
    birthdays in the next 7 days. It restricts the number of requests to no more than 10 per minute.

    :param current_user: The current user. Defaults to Depends(auth_service.get_current_user).
    :type current_user: UserModel
    :param db: The database session.
    :type db: Session
    :return: A list of contacts with upcoming birthdays.
    :rtype: list[ContactResponse]

    """
    today = datetime.now().date()
    end_date = today + timedelta(days=7)
    birthdays = await repository_contacts.get_birthdays(today, end_date, current_user, db)
    return birthdays


# @router.get("/", response_model=List[ContactResponse], description='No more than 10 requests per minute',
#             dependencies=[Depends(RateLimiter(times=10, seconds=60))])
@router.get("/", response_model=List[ContactResponse])
async def get_contacts(
        name: str = None, surname: str = None, email: str = None, phone: str = None, birthday: date = None,
        db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)
):
    """
    Route handler for retrieving contacts.
    This function handles GET requests to '/contacts/' for retrieving contacts based on specified criteria.
    It restricts the number of requests to no more than 10 per minute.

    :param name: The contact's name. Defaults to None.
    :type name: str
    :param surname: The contact's surname. Defaults to None.
    :type surname: str
    :param email: The contact's email. Defaults to None.
    :type email: str
    :param phone: The contact's phone. Defaults to None.
    :type phone: str
    :param birthday: The contact's birthday. Defaults to None.
    :type birthday: date
    :param current_user: The current user. Defaults to Depends(auth_service.get_current_user).
    :type current_user: UserModel
    :param db: The database session.
    :type db: Session
    :return: A list of contacts matching the specified criteria.
    :rtype: list[ContactResponse]

    """
    contacts = await repository_contacts.get_contacts(name, surname, email, phone, birthday, current_user, db)
    return contacts


# @router.post("/", response_model=ContactCreate, description='No more than 10 requests per minute',
#              dependencies=[Depends(RateLimiter(times=10, seconds=60))])
@router.post("/", response_model=ContactCreate)
async def create_contact(contact: ContactCreate, current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    """
    Route handler for creating contacts.
    This function handles POST requests to '/contacts/' for creating new contacts.
    It restricts the number of requests to no more than 10 per minute.

    :param contact: The contact data to create.
    :type contact: ContactCreate model.
    :param current_user: The current user.
    :type current_user: UserModel. Defaults to Depends(auth_service.get_current_user)
    :param db: The database session.
    :type db: Session
    :return: The created contact data.
    :rtype: Contact model

    """
    return await repository_contacts.create_contact(contact, current_user, db)


# @router.get("/{contact_id}", response_model=ContactResponse, description='No more than 10 requests per minute',
#             dependencies=[Depends(RateLimiter(times=10, seconds=60))])
@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    """
    Route handler for retrieving a specific contact.

    This function handles GET requests to '/contacts/{contact_id}' for retrieving a specific contact.
    It restricts the number of requests to no more than 10 per minute.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param current_user: The current user.
    :type current_user: UserModel. Defaults to Depends(auth_service.get_current_user)
    :param db: The database session.
    :type db: Session
    :return: The retrieved contact data.
    :rtype: ContactResponse form

    Raises:
    HTTPException: If the contact is not found.

    """
    contact = await repository_contacts.get_contact(contact_id, current_user, db)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


# @router.put("/{contact_id}", response_model=ContactResponse, description='No more than 10 requests per minute',
#             dependencies=[Depends(RateLimiter(times=10, seconds=60))])
@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: int, contact_update: ContactUpdate, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    Route handler for updating a specific contact.

    This function handles PUT requests to '/contacts/{contact_id}' for updating an existing contact.
    It restricts the number of requests to no more than 10 per minute.

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param contact_update: The updated contact data.
    :type contact_update: ContactUpdate model
    :param current_user: The current user. Defaults to Depends(auth_service.get_current_user)
    :type current_user: UserModel.
    :param db: The database session.
    :type db: Session
    :return: The updated contact data.
    :rtype: ContactResponse form

    Raises:
    HTTPException: If the contact is not found.

    """
    updated_contact = await repository_contacts.update_contact(contact_id, contact_update, current_user, db)
    if not updated_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return updated_contact


# @router.delete("/{contact_id}", description='No more than 10 requests per minute',
#                dependencies=[Depends(RateLimiter(times=10, seconds=60))])
@router.delete("/{contact_id}")
async def delete_contact(contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    Route handler for deleting a specific contact.

    This function handles DELETE requests to '/contacts/{contact_id}' for deleting a contact.
    It restricts the number of requests to no more than 10 per minute.

    :param contact_id: The ID of the contact to delete.
    :type contact_id: int
    :param current_user: The current user.
    :type current_user: UserModel. Defaults to Depends(auth_service.get_current_user)
    :param db: The database session.
    :type db: Session
    :return: A dictionary containing a success message.
    :rtype: dictionary

    Raises: HTTPException: If the contact is not found.

    """
    deleted_contact = await repository_contacts.delete_contact(contact_id, current_user, db)
    if not deleted_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"message": "Contact deleted successfully"}

