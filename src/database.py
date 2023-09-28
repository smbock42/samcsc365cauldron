import os
import dotenv
from sqlalchemy import create_engine

def database_connection_url():
    if dotenv.load_dotenv() == False:
        dotenv.load_dotenv(dotenv_path="test.env")

    return os.environ.get("POSTGRES_URI")

engine = create_engine(database_connection_url(), pool_pre_ping=True)