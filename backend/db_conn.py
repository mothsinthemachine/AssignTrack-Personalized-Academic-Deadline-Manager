import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Connect to the PostgreSQL database
def connect_to_db():
    # Get database URL from environment variable
    database_url = os.environ.get('DATABASE_URL')
    
    # Heroku's DATABASE_URL starts with "postgres://" but psycopg2 expects "postgresql://"
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    # Connect to the database
    conn = psycopg2.connect(database_url)
    return conn

if __name__=='__main__':
    connect_to_db()