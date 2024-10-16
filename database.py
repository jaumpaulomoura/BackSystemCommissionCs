from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import cx_Oracle
import psycopg2
from sqlalchemy import create_engine
import logging

# Configurações do Oracle
oracle_user = "PRODUCAO"
oracle_password = "a"
oracle_host = "192.168.1.62:1521/chbprd"

oracle_user_loja = "PRODUCAO"
oracle_password_loja = "a"
oracle_host_loja = "192.168.1.62:1521/ORCL"

# Configurações do PostgreSQL
postgres_user = "u13cacln8vgrti"
postgres_password = "pfeaadb47e0c224fa7efd121fc2aaef7dcb7425a36602d69b6bef5b247b747953"
postgres_host = "ec2-3-219-15-106.compute-1.amazonaws.com"
postgres_db = "dbhmk42rm7663c"
# Configuração do log
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
postgres_engine = create_engine(f'postgresql://{postgres_user}:{postgres_password}@{postgres_host}/{postgres_db}')
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configuração do banco de dados PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{postgres_user}:{postgres_password}@{postgres_host}/{postgres_db}'
    
    # Configuração do banco de dados Oracle
    oracle_uri = f'oracle+cx_oracle://{oracle_user}:{oracle_password}@{oracle_host}'
    app.config['SQLALCHEMY_BINDS'] = {
        'oracle': oracle_uri
    }
    
    db.init_app(app)

    return app, db






def connect_to_oracle():
    """Conecta ao banco de dados Oracle."""
    try:
        connection = cx_Oracle.connect(oracle_user, oracle_password, oracle_host)
        print("Conexão ao Oracle realizada com sucesso.")
        return connection
    except cx_Oracle.DatabaseError as e:
        print(f"Erro ao conectar ao Oracle: {e}")
        raise

def connect_to_oracle_loja():
    return cx_Oracle.connect(oracle_user_loja, oracle_password_loja, oracle_host_loja)

def connect_to_postgres():
    try:
        connection = psycopg2.connect(
            user=postgres_user,
            password=postgres_password,
            host=postgres_host,
            database=postgres_db
        )
        return connection
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        raise
