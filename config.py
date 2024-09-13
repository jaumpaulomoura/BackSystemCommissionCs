# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'a')  # Para JWT
