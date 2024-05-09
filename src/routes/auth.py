"""
Module for authentication routes.
"""

from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.email import send_email

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    Route handler for user signup.
    This function handles POST requests to '/auth/signup' for user registration.
    It checks if the user already exists, hashes the password, creates a new user,
    and sends a confirmation email using background tasks.

    :param body: The user data model containing username, email, and password.
    :type body: UserModel
    :param background_tasks: Background tasks for sending email.
    :type background_tasks: BackgroundTasks model
    :param request: The incoming request object.
    :type request: Request model
    :param db: The database session.
    :type db: Session
    :return: A dictionary containing the newly created user and a confirmation message.
    :rtype: dictionary

    Raises:
    HTTPException: If the account already exists.

    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)
    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Route handler for user login.
    This function handles POST requests to '/auth/login' for user login.
    It verifies the credentials, generates JWT tokens, and updates the refresh token.

    :param body: The login form data. Defaults to Depends().
    :type body: OAuth2PasswordRequestForm, optional
    :param db: The database session.
    :type db: Session
    :return: A dictionary containing the access token, refresh token, and token type.
    :rtype: dictionary

    Raises:
    HTTPException: If the email is invalid, not confirmed, or the password is incorrect.

    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    Route handler for token refresh.
    This function handles GET requests to '/auth/refresh_token' for token refresh.
    It verifies the refresh token, generates new access and refresh tokens, and updates
    the refresh token in the database.

    :param credentials: The HTTP authorization credentials. Defaults to Security(security).
    :type credentials: HTTPAuthorizationCredentials, optional
    :param db: The database session. Defaults to Depends(get_db).
    :type db: Session
    :return: A dictionary containing the access token, refresh token, and token type.
    :rtype: dictionary

    Raises:
    HTTPException: If the refresh token is invalid.

    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Route handler for confirming user email addresses.
    This function handles GET requests to '/auth/confirmed_email/{token}' for confirming
    user email using the verification token.

    :param token: The verification token.
    :type token: str
    :param db: The database session. Defaults to Depends(get_db).
    :type db: Session
    :return: A dictionary containing a confirmation message.
    :rtype: dictionary

    Raises:
    HTTPException: If there is a verification error.

    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    """
    Route handler for requesting confirmation emails.

    This function handles POST requests to '/auth/request_email' for requesting
    confirmation emails. It sends a confirmation email if the user email is not
    already confirmed.
    :param body: The request email data model.
    :type body: RequestEmail data model
    :param background_tasks: Background tasks for sending email.
    :type background_tasks: BackgroundTasks data model
    :param request: Background tasks for sending email.
    :type request: BackgroundTasks data model
    :param db: The database session.
    :type db: Session
    :return: A dictionary containing a confirmation message.
    :rtype: dictionary

    """
    user = await repository_users.get_user_by_email(body.email, db)
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}
