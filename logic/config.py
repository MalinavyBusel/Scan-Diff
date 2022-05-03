import os

from pydantic import BaseSettings
from decouple import config


class ServerSettings(BaseSettings):
    HOST = 'localhost'
    PORT = 5000
    DEBUG = False
    SECRET_KEY = config('KEY', cast=str)


class LogicSettings(BaseSettings):
    TESSERACT = config('TESSERACT_LOCATION', cast=str)


class Settings(ServerSettings, LogicSettings):
    pass


settings = Settings()
