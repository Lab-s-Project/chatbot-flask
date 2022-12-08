import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote

def get_connection():
    _username=os.environ.get('DB_USERNAME')
    _password=os.environ.get('DB_PASSWORD')
    _port=os.environ.get('DB_PORT')
    _db_name=os.environ.get('DB_NAME')
    _host=os.environ.get('DB_HOST')

    db_connection_string = f'mysql+pymysql://{_username}:%s@{_host}:{_port}/{_db_name}' % quote(_password)
    # db_connection = create_engine(db_connection_string)
    # Session.configure(bind=db_connection)

    return db_connection_string