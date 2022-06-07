from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =  'postgresql://postgres:12345@localhost/jtatravel'
app.config['SECRET_KEY'] = '987456123'


# file uploading settings
app.config['FILE_UPLOADS_LIQUIDATION'] = 'F:\\Python Repo\\web database\\jtaflask\\jta web database\\main\\Files_Uploads\\Liquidation'

app.config['FILE_UPLOADS_FOR_LEAVES'] = 'F:\\Python Repo\\web database\\jtaflask\\jta web database\\main\\Files_Uploads\\Leave_Docs'

app.config['ALLOWED_FILE_EXTENSIONS'] = ['PNG', 'JPG', 'JPEG' , 'GIF', 'PDF','DOC', 'DOCX']

#app.config['MAX_CONTENT_LENGTH'] = 1024

db=SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'
login_manager.login_message = 'Please First Login For Accesing that Functonality'
login_manager.login_message_category = 'info'

#print(app.config)
from main import routes
from main import models
from main.routing import routing_test
from main import usefull_functions

