from dotenv import load_dotenv
from os import getenv
from app import app
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = getenv(
    'DATABASE_URL').replace('://', 'ql://', 1)
db = SQLAlchemy(app)
