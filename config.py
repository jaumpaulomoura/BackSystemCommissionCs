import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'a')  # Para JWT

    SMTP_SERVER = 'mail.carmensteffens.com.br'
    SMTP_PORT = 587
    SMTP_USERNAME = 'joao.paulo@carmensteffens.com.br'
    SMTP_PASSWORD = 'JoaoC$0508'  
