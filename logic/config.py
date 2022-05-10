import os

from pydantic import BaseSettings
from decouple import config


class ServerSettings(BaseSettings):
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = False
    SECRET_KEY = 'SECRET_KEY'


class LogicSettings(BaseSettings):
    TESSERACT = config('TESSERACT_LOCATION', cast=str)


class Settings(ServerSettings, LogicSettings):
    pass


settings = Settings()
