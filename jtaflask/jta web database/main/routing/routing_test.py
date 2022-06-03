from cgi import print_form
from dataclasses import dataclass
from tkinter import TRUE
from click import edit
from numpy import concatenate
from flask import session
from datetime import timedelta
from sqlalchemy import values
from sqlalchemy import func
from sqlalchemy.orm import column_property
from main import app
from main.models import *
#from main.forms import DeleteForm, UsersForm, LoginForm, AssetsForm
from main.forms import *
from main import db
from flask_login import login_user, logout_user, login_required, current_user
from io import BytesIO
#import also models
from flask import render_template, redirect, url_for, flash, request, send_from_directory, abort, send_file, jsonify
import os
from werkzeug.utils import secure_filename
import werkzeug

from main.usefull_functions import file_ext


@app.route('/home')
@app.route('/')
def home():
	page_title = 'Home Page'
	room_list = [
		{ "room": 859
		,
			"use": "reception",
			"sq-ft": 50,
			"price": 75
		},
		{ "room": 101,
			"use": "waiting",
			"sq-ft": 250,
			"price": 75
		},
		{ "room": 102,
			"use": "examination",
			"sq-ft": 125,
			"price": 150
		},
		{ "room": 103,
			"use": "examination",
			"sq-ft": 125,
			"price": 150
		},
		{ "room": 104,
			"use": "office",
			"sq-ft": 150,
			"price": 100
		},
		{ "room": 100,
			"use": "reception",
			"sq-ft": 50,
			"price": 75
		},
		{ "room": 101,
			"use": "waiting",
			"sq-ft": 250,
			"price": 75
		},
		{ "room": 102,
			"use": "examination",
			"sq-ft": 125,
			"price": 150
		},
		{ "room": 103,
			"use": "examination",
			"sq-ft": 125,
			"price": 150
		},
		{ "room": 104,
			"use": "office",
			"sq-ft": 150,
			"price": 100
		},
		{ "room": 100,
			"use": "reception",
			"sq-ft": 50,
			"price": 75
		},
		{ "room": 101,
			"use": "waiting",
			"sq-ft": 250,
			"price": 75
		},
		{ "room": 102,
			"use": "examination",
			"sq-ft": 125,
			"price": 150
		},
		{ "room": 103,
			"use": "examination",
			"sq-ft": 125,
			"price": 150
		},
		{ "room": 104,
			"use": "office",
			"sq-ft": 150,
			"price": 100
		},
		{ "room": 100,
			"use": "reception",
			"sq-ft": 50,
			"price": 75
		},
		{ "room": 101,
			"use": "waiting",
			"sq-ft": 250,
			"price": 75
		},
		{ "room": 102,
			"use": "examination",
			"sq-ft": 125,
			"price": 150
		},
		{ "room": 103,
			"use": "examination",
			"sq-ft": 125,
			"price": 150
		},
		{ "room": 104,
			"use": "office",
			"sq-ft": 150,
			"price": 100
		}
		
	]
	return render_template('home.html', title=page_title, room_list=room_list)