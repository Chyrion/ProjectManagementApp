from dotenv import load_dotenv
from os import getenv
from app import app
from flask_sqlalchemy import SQLAlchemy

load_dotenv()
# This top option is for deploying to fly
# In development it breaks the thing that it fixes in production
# app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URL').replace('://', 'ql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URL')
db = SQLAlchemy(app)
