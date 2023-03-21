from os import getenv
from dotenv import load_dotenv
from flask import Flask

load_dotenv()
app = Flask(__name__)
app.secret_key = getenv('SECRET_KEY')

import routes