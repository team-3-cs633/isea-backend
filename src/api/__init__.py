import secrets
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from dotenv import load_dotenv


load_dotenv()


APPLICATION_URL = os.getenv("APPLICATION_URL")
USER_ROLE_UUID = os.getenv("USER_ROLE_UUID")
ADMIN_ROLE_UUID = os.getenv("ADMIN_ROLE_UUID")
COORDINATOR_ROLE_UUID = os.getenv("COORDINATOR_ROLE_UUID")
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


local_environment = False
app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_urlsafe()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data/data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)


from api import routes
from api import models
