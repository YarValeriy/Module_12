from pydantic import EmailStr
from pydantic_settings import BaseSettings


# class Settings(BaseSettings, extra='allow'):
#     sqlalchemy_database_url: str
#     secret_key: str
#     algorithm: str
#     mail_username: EmailStr
#     mail_password: str
#     mail_from: str
#     mail_port: int
#     mail_server: str
#     redis_host: str = 'localhost'
#     redis_port: int = 6379
#     cloudinary_name: str
#     cloudinary_api_key: str
#     cloudinary_api_secret: str
#
#     class Config:
#         env_file = ".env"
#         env_file_encoding = "utf-8"
#
#
class Settings(BaseSettings, extra='allow'):
    sqlalchemy_database_url: str = 'postgresql+psycopg2://postgres:567234@localhost:5432/rest_app'
    secret_key: str = 'secret_key'
    algorithm: str = "HS256"
    mail_username: EmailStr = 'project_it@meta.ua'
    mail_password: str = 'goit_project'
    mail_from: str = 'project_it@meta.ua'
    mail_port: int = 465
    mail_server: str = 'smtp.meta.ua'
    redis_host: str = 'localhost'
    redis_port: int = 6379
    cloudinary_name: str = 'dhnuybjrj'
    cloudinary_api_key: str = '816415195945773'
    cloudinary_api_secret: str = 'ukVWJuTpzRkTsp50-WAU10bRa7U'

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

