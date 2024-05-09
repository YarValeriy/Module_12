"""
Module for user routes.

This module defines routes related to managing user profiles and avatars using the FastAPI `APIRouter`.
It includes routes for retrieving user details, and updating user avatars.
It imports necessary modules and dependencies including APIRouter, Depends, status, UploadFile, File,
Session, cloudinary, cloudinary.uploader, get_db, User, repository_users, auth_service, settings, and UserDb.
The `router` instance is created with a prefix of '/users' and tagged as "users".
The `read_users_me` route handler handles GET requests to '/users/me/' for retrieving details of the current user.
The `update_avatar_user` route handler handles PATCH requests to '/users/avatar' for updating the avatar of the current user.

"""

from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader
from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings
from src.schemas import UserDb

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    Route handler for retrieving user details.

    This function handles GET requests to '/users/me/' for retrieving details of the current user.

    :param current_user: The current user. Defaults to Depends(auth_service.get_current_user).
    :type current_user: User model
    :return: Details of the current user.
    :rtype: User model

    """
    return current_user


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    """
    Route handler for updating user avatar.
    This function handles PATCH requests to '/users/avatar' for updating the avatar of the current user.

    :param file: The avatar file to upload. Defaults to File().
    :type file: UploadFile. Defaults to File().
    :param current_user: The current user. Defaults to Depends(auth_service.get_current_user).
    :type current_user: User model
    :param db: The database session.
    :type db: Session
    :return: Updated details of the current user with the new avatar.
    :rtype: UserDb

    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'ContactsApp/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'ContactsApp/{current_user.username}')\
                        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user

