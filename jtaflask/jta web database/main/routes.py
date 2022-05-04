from dataclasses import dataclass
from numpy import concatenate
from flask import session
from datetime import timedelta
from sqlalchemy import values
from main import app
from main.models import *
#from main.forms import DeleteForm, UsersForm, LoginForm, AssetsForm
from main.forms import *
from main import db
from flask_login import login_user, logout_user, login_required, current_user
from io import BytesIO
#import also models
from flask import render_template, redirect, url_for, flash, request, send_from_directory, abort, send_file
import os
from werkzeug.utils import secure_filename
import werkzeug

from main.usefull_functions import file_ext

@app.route('/home')
@app.route('/')
def home():
	
	
	page_title = 'Home Page'
	room_list = [
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

@app.route('/about')
def about():
		room_list = [
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
		return render_template('about.html', room_list=room_list)


@app.route('/employees', methods=['GET','POST'])
def employees():
	deleteform = DeleteForm()
	if request.method=="POST":
		#print(request.form.get('delete_emp'))
		#print(type(request.form.get('delete_emp')))
		delete_employee = Users.query.filter_by(id=int(request.form.get('delete_emp'))).delete()
		#print(delete_employee)
		db.session.commit()
		flash('Employee Deleted Succesfully', category='primary' )

	
	emp = Users.query.all()

	return render_template('employee.html', emp = emp, title='Employees', deleteform=deleteform)


@app.route('/cars')
def cars_page():
		page_title= 'Cars'
		return render_template('cars.html', title=page_title)

@app.route('/assets', methods=['GET', 'POST'])
def assets_page():
	edit_asset_form = Assets_Edit_Form()
	
	
	if request.method=="POST":
		
		#print(request.form.get('delete_emp'))
		#print(type(request.form.get('delete_emp')))
		edit_asset = Assets.query.filter_by(id=int(request.form.get('asset_edit'))).first()		
		print(edit_asset.owner)
		print(edit_asset_form.owner.data.split())

		ownername = Users.query.filter_by(name = edit_asset_form.owner.data.split()[0]).filter_by(surname = edit_asset_form.owner.data.split()[1]).first()

		print(ownername)
		edit_asset.owner = ownername.id
		db.session.commit()
		flash('OwnerShip Granted Succesfully', category='primary' )	


	
	page_title='Assets'
	assets_available = Assets.query.all()
	return render_template('assets.html', title=page_title, assets=assets_available, edit_asset_form=edit_asset_form)


@app.route('/card_p_returns')
def card_returns():
		page_title='Card P.Returns'
		return render_template('card_p_canc.html', title=page_title)

@app.route('/daily_liquidation', methods=['GET','POST'])
def daily_liquidation():
	edit_form = Liquidation_Form()
	page_title= 'Daily Liquidation'
	
	if current_user.role=='Representative':	
		user_daily_liq = DailyLiquidation.query.filter(DailyLiquidation.owner ==current_user.id).all()		
		#user_daily_liq = db.session.query(DailyLiquidation.id, DailyLiquidation.total_sales).filter(DailyLiquidation.owner ==current_user.id ).all()
		print(user_daily_liq[0].confirm)

		return render_template('daily_liquidation.html', title = page_title, ownwed_daily_liqu = user_daily_liq , edit_form=edit_form)
	
	elif current_user.role=='Administrator' or'Office Staff':
		user_daily_liq = db.session.query(DailyLiquidation.id,
											DailyLiquidation.total_sales,
											DailyLiquidation.bank_deposit,
											DailyLiquidation.visa_transaction,
											DailyLiquidation.pre_cancels,
											DailyLiquidation.cancelled_tickets,
											DailyLiquidation.total_calculated_amount,
											DailyLiquidation.date_time_actual,
											DailyLiquidation.date_liquidated,
											DailyLiquidation.bank_dep_image,
											DailyLiquidation.jcc_daily_batch_image,
											DailyLiquidation.canceled_ticket_image,
											DailyLiquidation.daily_liquidation_balance,
											DailyLiquidation.remarks,
											DailyLiquidation.confirm,
											Users.name.label('fname'),
											Users.surname.label('surname')).outerjoin(Users, Users.id == DailyLiquidation.owner).order_by(DailyLiquidation.id.desc())
											
		# # edit liquidation										   
		# if request.method=="POST":
		# 	if request.form['submit_button'] == 'Save':
		# 		liq = db.session.query(DailyLiquidation).filter(DailyLiquidation.id==item.id).one() 
		# 		print(liq.id, liq.owner)

		
		#user_daily_liq = DailyLiquidation.query.all()
		return render_template('daily_liquidation.html', title = page_title, ownwed_daily_liqu = user_daily_liq, edit_form=edit_form )

	return render_template('daily_liquidation.html', title=page_title, edit_form=edit_form)

@app.route('/edit_daily_liquidation/<int:id>', methods=['GET','POST'])
def edit_daily_liquidation(id):
	print(id)
	edit_liq = db.session.query(DailyLiquidation).filter(DailyLiquidation.id==id).first()
	form = Liq_Edit_Form(formdata=request.form, obj=edit_liq)

	
	print(edit_liq.total_sales)
	print(edit_liq.bank_deposit)
	print(edit_liq.owner)

	return render_template('edit_daily_liq.html', title = 'Edit Daily Liq.', form=form)


@app.route('/add_daily_liquidation', methods=['GET','POST'])
def add_daily_liquidation():
	form = Liquidation_Form()
	
	if request.method=="POST":		
		'''
		file size
		len(form.bank_dep_image.data.read())
		'''
		if form.total_sales.data != (form.bank_deposit.data + form.visa_amount.data + form.precancels.data):
			flash(f'You Cannot Send Not Balanced Liquidation', category='danger' )
	
			
		else:
			#request.files['jcc_daily_image'].filename)
			print('my form files')
			print(request.files)
			file_names_dict={}
			for key, value in request.files.items():
				
				if not 'application/octet-stream' in value.content_type:
					#file_s = request.files['jcc_daily_image']
					file_s = request.files[key]
					print('this is my file')
					print(file_s)
					if not file_s.filename:
						flash(f'You cant Upload a file with out a name', category='danger' )
						return redirect(request.url)
					
					if not usefull_functions.allowed_files_ext(file_s.filename):
						flash(f'You cant Upload a file with that extension', category='danger' )
						return redirect(request.url)
					
					else:
						#filename = current_user.surname + '12_4_2022_' +  secure_filename(file_s.filename)
						filename = current_user.surname+ '_' + usefull_functions.file_rename_date()+ '_' + key + file_ext(file_s.filename)
						
						#file_s.save(os.path.join(app.config['FILE_UPLOADS_LIQUIDATION'], file_s.filename))
						file_s.save(os.path.join(app.config['FILE_UPLOADS_LIQUIDATION'], filename))
						file_names_dict[key] = f'{filename}'
			
					print(file_names_dict)
					print(len(file_names_dict))


				else:
					file_s = request.files[key]
					print('this is my file')
					print(file_s)
					if not file_s.filename:
						flash(f'You cant Upload a file with out a name', category='danger' )
						return redirect(request.url)
					
					if not usefull_functions.allowed_files_ext(file_s.filename):
						flash(f'You cant Upload a file with that extension', category='danger' )
						return redirect(request.url)
					
					else:
						#filename = current_user.surname + '12_4_2022_' +  secure_filename(file_s.filename)
						filename = current_user.surname+ '_' + usefull_functions.file_rename_date() +'_' + key + file_ext(file_s.filename)
						
						#file_s.save(os.path.join(app.config['FILE_UPLOADS_LIQUIDATION'], file_s.filename))
						file_s.save(os.path.join(app.config['FILE_UPLOADS_LIQUIDATION'], filename))
						file_names_dict[key] = f'{filename}'
			
					print(file_names_dict)
					print(len(file_names_dict))

			if 	len(file_names_dict) == 2:
				daily_liq_create = DailyLiquidation(
								total_sales= form.total_sales.data,
								bank_deposit = form.bank_deposit.data,
								visa_transaction = form.visa_amount.data,
								pre_cancels = form.precancels.data,
								cancelled_tickets = form.canceled_tickets.data,
								bank_dep_image = file_names_dict['bank_dep_image'],
								total_calculated_amount = form.total_sales.data - (form.bank_deposit.data + form.visa_amount.data + form.precancels.data),
								jcc_daily_batch_image = file_names_dict['jcc_daily_image'],							
								remarks = form.remarks.data,
								daily_liquidation_balance = form.total_sales.data - (form.bank_deposit.data + form.visa_amount.data + form.precancels.data),
								owner = current_user.id
								)
				db.session.add(daily_liq_create)
				db.session.commit()
				return(redirect(url_for('daily_liquidation')))
			
			elif len(file_names_dict) == 3:
				daily_liq_create = DailyLiquidation(
								total_sales= form.total_sales.data,
								bank_deposit = form.bank_deposit.data,
								visa_transaction = form.visa_amount.data,
								pre_cancels = form.precancels.data,
								cancelled_tickets = form.canceled_tickets.data,
								bank_dep_image = file_names_dict['bank_dep_image'],
								total_calculated_amount = form.total_sales.data - (form.bank_deposit.data + form.visa_amount.data + form.precancels.data),
								jcc_daily_batch_image = file_names_dict['jcc_daily_image'],
								canceled_ticket_image = file_names_dict['cancelled_tickets_image'],
								remarks = form.remarks.data,
								daily_liquidation_balance = form.total_sales.data - (form.bank_deposit.data + form.visa_amount.data + form.precancels.data),
								owner = current_user.id
								)
				db.session.add(daily_liq_create)
				db.session.commit()
				return(redirect(url_for('daily_liquidation')))
			return(redirect(url_for('daily_liquidation')))

	return render_template('add_daily_liqui.html', title = 'Daily Liq.', form=form)

@app.route('/confirm_daily_liquidation/<int:id>', methods=['GET','POST'])
def confirm_daily_liquidation(id):
	print(id)
	day_liq = db.session.query(DailyLiquidation).filter(DailyLiquidation.id==id).one()
	print(day_liq)
	day_liq.confirm=True
	db.session.commit()
	flash(f'Liquidation Confirmed Succesfully', category='primary' )	
	return redirect(url_for('daily_liquidation'))

@app.route('/add_user', methods=['GET','POST'])
#@login_required
def add_user():		
	form = UsersForm()
	if form.validate_on_submit():
		user_create=Users(name= form.name.data,
						  surname= form.surname.data,						  
						  #username = form.username.data,
						  email= form.email.data,
						  password= form.password.data,
						  active = form.active.data,
						  role = form.role.data

							)
		db.session.add(user_create)
		db.session.commit()

		#print(user_create)
		flash(f'User {form.name.data} {form.surname.data} Created Succesfully', category='primary' )
		return redirect(url_for('add_user'))

	if form.errors != {}:
		for error_msg in form.errors.values():
			flash(f'Error!!! {error_msg[0]}', category='danger' )
		print('form errors')

	

	return render_template('add_user_form.html', form = form, title='Add a User')



@app.route('/test')
def test_home():  
		page_title= 'Test'

		return render_template('test.html')

@app.route('/login', methods=['GET' , 'POST'])
def login_page():
	session.permanent = True
	app.permanent_session_lifetime = timedelta(minutes=30)
	form = LoginForm()
	if form.validate_on_submit():
		attempted_user = Users.query.filter_by(email = form.email.data).first()
		
		if not attempted_user:
			flash(f'No Account Founded in Database. Please Contact Site Administrator', category='warning')
		elif attempted_user.active == False:
			flash(f'Your Account Is Inactive. Please Contact Site Administrator', category='warning')

		elif attempted_user and attempted_user.check_password_correction(attempted_password = form.password.data):
			login_user(attempted_user)
			print(f'User Role: {attempted_user.role} {attempted_user.name} {attempted_user.surname}')

			flash(f'Login Succesfully as {attempted_user.name} {attempted_user.surname}', category='success')
			return redirect(url_for('home'))
		else:			
			flash(f'Wrong Email or Password', category='danger')

	return render_template('login.html', title = 'Login', form = form)

@app.route('/logout')
def logout_page():
	logout_user()
	flash('You have been loged out!', category='info')
	return redirect(url_for('login_page'))


@app.route('/add_asset', methods=['GET','POST'])
#@login_required
def add_asset():
	form = AssetsForm()
	
	if form.validate_on_submit():
		asset_create= Assets(name = form.name.data
						#   surname= form.surname.data,						  
						#   #username = form.username.data,
						#   email= form.email.data,
						#   password= form.password.data,
						#   active = form.active.data,
						#   role = form.role.data

							)
		db.session.add(asset_create)
		db.session.commit()

		#print(user_create)
		flash(f'Asset {form.name.data} Created Succesfully', category='primary' )
		return redirect(url_for('assets_page'))
	
	if form.errors != {}:
		for error_msg in form.errors.values():
			flash(f'Error!!! {error_msg[0]}', category='danger' )
		print('form errors')
		return redirect(url_for('add_asset'))
	
	return render_template('add_asset.html', title = 'Add Asset', form = form)


'''
string
int
float
path
uuid
'''
@app.route('/down-file/<string:file_name>', methods=['GET','POST'])
def down_file(file_name):
	print(file_name)
	print(app.config['FILE_UPLOADS_LIQUIDATION'])
	try:
		return send_from_directory(app.config['FILE_UPLOADS_LIQUIDATION'],path=file_name, as_attachment=True)

	except FileNotFoundError:
		print('abort')
		abort(404)
	 

@app.route('/testing', methods=['GET','POST'])
def test():
	emp = Users.query.all()
	return render_template('test_table_boot_code.html', emp = emp)