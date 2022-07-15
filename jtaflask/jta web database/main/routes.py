from dataclasses import dataclass
from itertools import groupby
from turtle import title
from typing import final
from unicodedata import category
from numpy import concatenate
import numpy as np
from flask import session
from datetime import timedelta,date
from sqlalchemy import desc, null, values
from sqlalchemy import func, or_
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

def count_annual_leaves(id) ->list:
	'''Function to take  employee id and calculates the total of annual leaves that should be taken  and how many is taken
	return total from begining, total taken from begining, remains
	[51.26301369387, 20.5, 30.76301369387]
	'''

	user_is = db.session.query(Users.name, Users.surname, Users.registration_date).filter(Users.id==id, Users.active==True).one()
	
	#total annual taken from all entries
	total_annual_taken = db.session.query(db.func.sum(Leaves.total)).filter( Leaves.owner == id, Leaves.reason=='Annual Leave' ).first()
	
	start = user_is.registration_date
	end = date.today()
	total_worked_days_from_begining = usefull_functions.leave_days(start, end, holidays=[])[3]

	annual_total_from_begining = total_worked_days_from_begining * 0.05753424657
	try:
		remaining = annual_total_from_begining - total_annual_taken[0]
	except TypeError:
		remaining = annual_total_from_begining - 0

	return [annual_total_from_begining, total_annual_taken[0], remaining ]
def statistics_current_year(id)->dict:
	'''Function to take  employee id and annual leave current year total
		totals = {'Annual Leave' : 0.0, 'Military' : 0.0, 'Sick - Leave' : 0.0, 'UnPaid': 0.0, 'Working-Off' : 0.0, 'Working-On' : 0.0, 
		'Public-On' : 0.0, 'Public-Off' : 0.0, 'Other' : 0.0}	'''
	'''select extract(year from to_) from leaves
					where owner=4;'''
	year = usefull_functions.current_date()[-4:]

	
	years_from = db.session.query(db.func.extract('year', Leaves.from_)).filter(Leaves.owner == id).all()
	years_to = db.session.query(db.func.extract('year', Leaves.to_)).filter(Leaves.owner == id).all()
	
	years_from_list=[str(item[0])[:-2] for item in years_from]
	years_to_list = [str(item[0])[:-2] for item in years_to]
	all_years_list = years_from_list + years_to_list
	all_years_list = usefull_functions.years_uniques(all_years_list)
	

	#user_is = db.session.query(Users.name, Users.surname, Users.registration_date).filter(Users.id==id, Users.active==True).one()
	#DATE_PART('year',  from_) = 2022
	#a = db.session.query(db.func.date_part(year, Leaves.from_)==str(year)).filter( Leaves.owner == id, Leaves.reason=='Annual Leave',  ).first()
	years_stat=[]
	for year in all_years_list:
		total_for_current_year = db.session.query(Leaves.from_, Leaves.to_, Leaves.reason, Leaves.country,Leaves.total).filter(or_(db.func.date_part('year', Leaves.from_)==year,
		db.func.date_part('year', Leaves.to_)==year), 
		Leaves.owner==id, Leaves.confirm!="false").all()		
		
		totals = {'Year':year,'Annual Leave' : 0.0, 'Military' : 0.0, 
				  'Sick - Leave' : 0.0, 'UnPaid': 0.0, 'Working-Off' : 0.0, 'Working-On' : 0.0, 'Public-On' : 0.0, 'Public-Off' : 0.0, 'Other' : 0.0}
		for item in total_for_current_year:	

			for key in totals:
				if (year != item[0].strftime("%Y") or year != item[1].strftime("%Y")):
					#MAKE A LIST WITH ALL PUBLIC HOLIDAYS
					holidays:list = usefull_functions.days_period(db.session.query(func.to_char(PublicHolidays.date_of_holiday,'yyyy-mm-dd')).filter(PublicHolidays.country == item[3]).all())
					
					dd = [item[0] + timedelta(days=x)  for x in range((item[1]-item[0]).days + 1) if (item[0] + timedelta(days=x)).strftime("%Y")==year]
					start = dd[0]
					end = dd[-1]
				
					total = usefull_functions.leave_days(start, end, holidays)[0]
				
					
					if key == item.reason:
						totals[key] = totals[key] + total
				
				else:
					if key == item.reason:
						totals[key] = totals[key] + item.total
		years_stat.append(totals)
			

	return years_stat
def leave_hist_add():
	'''Function that returns the latest entrie for leaves
	We will use it to grap the latest id so we can use it for inserting in leaves history'''
	
	leave_h = db.session.query(func.max(Leaves.id)).first()
	return leave_h[0]
def file_returner(request, file_name_details):
	
	file_names_dict={}
	for key, value in request.files.items():
		
		if not 'application/octet-stream' in value.content_type:
			#file_s = request.files['jcc_daily_image']
			file_s = request.files[key]			
			print(file_s)
			if not file_s.filename:
				flash(f'You cant Upload a file with out a name', category='danger' )
				return redirect(request.url)
			
			if not usefull_functions.allowed_files_ext(file_s.filename):
				flash(f'You cant Upload a file with that extension', category='danger' )
				return redirect(request.url)
			
			else:
				#filename = current_user.surname + '12_4_2022_' +  secure_filename(file_s.filename)
				filename = file_name_details['Employee'].split()[0]+ '_' +file_name_details['Employee'].split()[1]+ '_'+'Batch_'+ file_name_details['batch']+ '_'+'ticket_'+ file_name_details['ticket'] + file_ext(file_s.filename)
				
				#file_s.save(os.path.join(app.config['FILE_UPLOADS_LIQUIDATION'], file_s.filename))
				file_s.save(os.path.join(app.config['FILE_UPLOADS_FOR_CARDS'], filename))
				file_names_dict[key] = f'{filename}'

			return file_names_dict

def contract_save(request, file_name_details):
	file_names_dict={}
	print(request.files.items())
	
	for key, value in request.files.items():
		
		if not 'application/octet-stream' in value.content_type:
			#file_s = request.files['jcc_daily_image']
			file_s = request.files[key]			
			print(file_s)
			
			if not file_s.filename:
				flash(f'You cant Upload a file with out a name', category='danger' )
				return redirect(request.url)
			
			if not usefull_functions.allowed_files_ext(file_s.filename):
				flash(f'You cant Upload a file with that extension', category='danger' )
				return redirect(request.url)
			
			else:
				#filename = current_user.surname + '12_4_2022_' +  secure_filename(file_s.filename)
				filename = file_name_details + file_ext(file_s.filename)
				
				#file_s.save(os.path.join(app.config['FILE_UPLOADS_LIQUIDATION'], file_s.filename))
				file_s.save(os.path.join(app.config['FILE_UPLOADS_CAR_CONTRACTS'], filename))
				file_names_dict[key] = f'{filename}'

			return file_names_dict






def active_reps_for_forms()->list:
	'''Return the active reps as list of strings containig Name and Surname of each rep '''
	reps = db.session.query(Users).filter(Users.
	position=='Representative', Users.active == True).order_by(Users.name).all()
	
	reps_for_form = [f'{rep.name} {rep.surname}' for rep in reps]		
	return reps_for_form
def asset_category_all()-> list:
	'''Function To Return in A list all the asset categories'''
	categories = AssetCategory.query.all()
	all_categories = [category.category for category in categories]
	all_categories.sort()
	return all_categories
def all_users_forms() ->list:
	all_users = db.session.query(Users).filter(Users.active == True).order_by(Users.name).all()
	reps_for_form = [f'{user.name} {user.surname}' for user in all_users]		
	return reps_for_form
def rent_asset(asset_rent_form,request):
		owner =db.session.query(Users.id).filter(Users.name == request.get('employee').split()[0], Users.surname == request.get('employee').split()[1]).first()
		
		
		add_rented_history=AssetRentedHistory(asset=request.get('asset_rental_id'),given_out = request.get('given_out'),owner=owner[0],date = asset_rent_form.date.data,remarks = asset_rent_form.remarks.data)

		asset_update = db.session.query(Assets).filter(Assets.id == request.get('asset_rental_id')).first()
		
		asset_update.status=request.get('given_out')
		db.session.add(asset_update)
		
		db.session.add(add_rented_history)
		
		db.session.commit()
		return flash(f'Asset Rented Succesfully', category='primary' )
def all_assets_rented(id=None):
	

	asset_owned = Assets.query.filter(Assets.status=='out').all()

	final_all_report=[]
	for asset in asset_owned:

		rented_h = db.session.query(column_property(func.to_char(AssetRentedHistory.date, 'DD/MM/YYYY').label('date')),AssetRentedHistory.asset,AssetRentedHistory.remarks,AssetRentedHistory.given_out,Users.name,Users.surname).filter(asset.id==AssetRentedHistory.asset).outerjoin(Users,AssetRentedHistory.owner==Users.id).order_by(AssetRentedHistory.id.desc()).first()
		
		

		final_all_report.append({'owner':rented_h.name+" " + rented_h.surname, 'asset':[asset.serial_number,asset.category,asset.value,rented_h.date, rented_h.remarks, rented_h.given_out, rented_h.asset] })
	
	
	if id != None:
		emp= Users.query.filter(Users.id==id).first()

		final_per_person_asset=[]
		for item in final_all_report:
			if item['owner'] == f'{emp.name} {emp.surname}':
				final_per_person_asset.append(item)
		return(final_per_person_asset)
	
	else:
		return final_all_report


#print(all_assets_rented())


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



@app.route('/card_returns',methods=['GET', 'POST'])
def card_returns():
	deleteform = DeleteForm()

	if request.method=="POST":
		if request.form['submit_button'] == "Delete":
			#print(request.form.get('delete_emp'))
			#print(type(request.form.get('delete_emp')))
		
			delete_employee = CardPaymentReturns.query.filter_by(id=int(request.form.get('delete_card'))).delete()
			
			db.session.commit()
			flash('Card Return Deleted Succesfully', category='primary' )


	#cards_table = CardPaymentReturns().query.all() 
	cards_table = db.session.query(CardPaymentReturns.id,							CardPaymentReturns.ticket_cancelled, 							CardPaymentReturns.excursion_name,								CardPaymentReturns.amount_returned,								CardPaymentReturns.clients_name,								CardPaymentReturns.batch_number,							CardPaymentReturns.docs,CardPaymentReturns.remarks,	
					CardPaymentReturns.previous_week, (column_property(func.to_char(CardPaymentReturns.cancelled_date, 'DD/MM/YYYY').label('cancelled_date'))),
					(column_property(func.to_char(CardPaymentReturns.booked_date, 'DD/MM/YYYY').label('booked_date'))),
					Users.name.label('fname'),
					Users.surname.label('surname')).outerjoin(Users, Users.id == CardPaymentReturns.owner).order_by(CardPaymentReturns.id.desc())
	
	

	return render_template('CardPaymentReturns/card_returns.html', title='Card P.Returns', cards_table =cards_table, deleteform=deleteform)

@app.route('/add_card_return',methods=['GET', 'POST'])
def add_card_return():
	form  = CardReturnsForm()	
	form.employee.choices = active_reps_for_forms()

	if request.method=="POST":
		file_name_details = {'Employee':form.employee.data, 'batch':form.batch_number.data, 'ticket':form.ticket_cancelled.data}
		
		file_name = file_returner(request, file_name_details)
		print(file_name)
		
		
		
		
		owner  = db.session.query(Users.id).filter(Users.name == form.employee.data.split()[0], Users.surname== form.employee.data.split()[1]).one()
		
		
		if form.previous_week.data=="Yes":
			previous_week = True
		else:
			previous_week=False

		if form.validate_on_submit():
			new_card_return = CardPaymentReturns(
				owner = owner[0],
				ticket_cancelled = form.ticket_cancelled.data,
				excursion_name = form.excursion_name.data,
				booked_date = form.booked_date.data,
				clients_name = form.clients_name.data,
				amount_returned = form.amount_returned.data,
				batch_number = form.batch_number.data,
				remarks = form.remarks.data,
				cancelled_date = form.cancelled_date.data,
				previous_week = previous_week,
				docs = file_name['docs']		

			)
			db.session.add(new_card_return)
			db.session.commit()

			return redirect(url_for("card_returns"))
	if form.errors != {}:
		for error_msg in form.errors.values():
			flash(f'Error!!! {error_msg[0]}', category='danger' )
	
	
	return render_template('CardPaymentReturns/add_card_return.html', form=form)

@app.route('/edit_card_return/<int:id>',methods=['GET', 'POST'])
def edit_card_return(id):

	edit_card = db.session.query(CardPaymentReturns).filter(CardPaymentReturns.id==id).first()	
	owner = db.session.query(Users).filter(edit_card.owner==Users.id).first()
	owner = f'{owner.name} {owner.surname}'
	active_reps = active_reps_for_forms()
	print(active_reps)
	print(active_reps.index(owner))
	if owner in active_reps:
		active_reps.insert(0,f'* {owner}')
		
	active_reps.pop(active_reps.index(owner))
	print(active_reps)
	
	form = CardReturnsFormEdit(formdata=request.form, obj=edit_card)

	form.employee.choices = active_reps 
	
	if form.validate_on_submit():
		

		if owner not in form.employee.data:
			print('No its not in')
			new_owner = db.session.query(Users).filter(Users.name==form.employee.data.split()[0], Users.surname==form.employee.data.split()[1]).first()
			#print(new_owner.id)
			edit_card.owner = new_owner.id
			owner = f'{form.employee.data.split()[0]} {form.employee.data.split()[1]}'
		

		
		for key, value in request.files.items():
			if not 'application/octet-stream' in value.content_type:
				usefull_functions.file_deleter(form.docs.data)
				file_name_details = {'Employee':owner, 'batch':form.batch_number.data, 'ticket':form.ticket_cancelled.data}
				file_name = file_returner(request, file_name_details)
				edit_card.docs = file_name['docs']


		edit_card.ticket_cancelled = form.ticket_cancelled.data
		edit_card.excursion_name = form.excursion_name.data
		edit_card.booked_date = form.booked_date.data
		edit_card.clients_name = form.clients_name.data
		edit_card.amount_returned = form.amount_returned.data
		edit_card.batch_number = form.batch_number.data
		edit_card.remarks = form.remarks.data
		edit_card.cancelled_date = form.cancelled_date.data
		if form.previous_week.data=='Yes':
			edit_card.previous_week = True
		else:
			edit_card.previous_week = False

		
		db.session.add(edit_card)
		db.session.commit()
		return redirect(url_for('card_returns'))

	if form.errors != {}:
		for error_msg in form.errors.values():
			flash(f'Error!!! {error_msg[0]}', category='danger' )


	return render_template('CardPaymentReturns/edit_card_return.html', title= "Edir Card Payment R.", form=form)


@app.route('/daily_liquidation', methods=['GET','POST'])
def daily_liquidation():
	edit_form = Liquidation_Form()
	page_title= 'Daily Liquidation'
	# already value to check if the user has already submited a liquidation for a day
	already= db.session.query(DailyLiquidation).filter(DailyLiquidation.date_time_actual== usefull_functions.current_date()).filter(DailyLiquidation.owner==current_user.id).count()
	
	if 'Representative' in current_user.role:	
		#user_daily_liq = DailyLiquidation.query.filter(DailyLiquidation.owner == current_user.id).all()		
		user_daily_liq = db.session.query(DailyLiquidation.id, DailyLiquidation.total_sales, DailyLiquidation.bank_deposit, DailyLiquidation.visa_transaction, DailyLiquidation.pre_cancels,DailyLiquidation.cancelled_tickets, DailyLiquidation.total_calculated_amount, 
		column_property(func.to_char(DailyLiquidation.date_time_actual, 'DD/MM/YYYY').label('date_time_actual')) ,
		#DailyLiquidation.date_time_actual,
		column_property(func.to_char(DailyLiquidation.date_liquidated,'DD/MM/YYYY').label('date_liquidated')),
		#DailyLiquidation.date_liquidated,
		
		DailyLiquidation.bank_dep_image, 
		DailyLiquidation.jcc_daily_batch_image,DailyLiquidation.canceled_ticket_image, DailyLiquidation.daily_liquidation_balance, DailyLiquidation.remarks,DailyLiquidation.confirm).filter(DailyLiquidation.owner ==current_user.id ).order_by(DailyLiquidation.id.desc())
		# if already:
		# 	flash(f'{current_user.name} {current_user.surname} you have Already submited a Daily Liquidation for Today {usefull_functions.current_date()}. For Any Help please Call Supervisor', category='info' )
		
		

		return render_template('daily_liquidation.html', title = page_title, ownwed_daily_liqu = user_daily_liq , edit_form=edit_form, already=already)
	
	elif 'Administrator' or'Office Staff' in current_user.role:
		user_daily_liq = db.session.query(DailyLiquidation.id,
											DailyLiquidation.total_sales,
											DailyLiquidation.bank_deposit,
											DailyLiquidation.visa_transaction,
											DailyLiquidation.pre_cancels,
											DailyLiquidation.cancelled_tickets,
											DailyLiquidation.total_calculated_amount,
											column_property(func.to_char(DailyLiquidation.date_time_actual, 'DD/MM/YYYY').label('date_time_actual')),
											#DailyLiquidation.date_time_actual,
											column_property(func.to_char(DailyLiquidation.date_liquidated,'DD/MM/YYYY').label('date_liquidated')),
											#DailyLiquidation.date_liquidated,
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

	
	'''
	we should update daily liquidation according user login
	if its admins they cant change file uploads
	if its users like reps they can change that files
	'''

	if 'Administrator' in current_user.role:		
		if form.validate_on_submit():
			if form.total_sales.data != (form.bank_deposit.data + form.visa_transaction.data + form.pre_cancels.data):
				flash(f'You Cannot Send Not Balanced Liquidation', category='danger' )
				flash(f'Current Balance is {form.total_sales.data - (form.bank_deposit.data + form.visa_transaction.data + form.pre_cancels.data)}', category='primary' )
			else:
				#sql injection
				edit_liq.total_sales = form.total_sales.data
				edit_liq.bank_deposit = form.bank_deposit.data
				edit_liq.visa_transaction = form.visa_transaction.data
				edit_liq.pre_cancels = form.pre_cancels.data
				edit_liq.cancelled_tickets = form.cancelled_tickets.data
				edit_liq.remarks = form.remarks.data
				db.session.add(edit_liq)
				db.session.commit()
				flash(f'Liquidation DB_ID_No:{id} Updated Succesfully', category='info')
				return (redirect(url_for('daily_liquidation')))
		if form.errors != {}:
			print (form.errors)

		return render_template('edit_daily_liq.html', title = 'Edit Daily Liq.', form=form)
	
	if current_user.role== 'Representative':		
		if form.validate_on_submit():

			if form.total_sales.data != (form.bank_deposit.data + form.visa_transaction.data + form.pre_cancels.data):
				flash(f'You Cannot Send Not Balanced Liquidation', category='danger' )
				flash(f'Current Balance is {form.total_sales.data - (form.bank_deposit.data + form.visa_transaction.data + form.pre_cancels.data)}', category='primary' )
			
			else:
				#print('my form files')
				#print(request.files)
				file_names_dict={}
				
				for key, value in request.files.items():
					print('inside dictionary build')
					#print('file value')
					#print(value.content_type)
					#print(type(value))
					if not 'application/octet-stream' in value.content_type:
						#file_s = request.files['jcc_daily_image']
						file_s = request.files[key]
						file_extension = file_ext(file_s.filename)
						#print('this is my file')
						#print(file_s)
						if not file_s.filename:
							flash(f'You cant Upload a file with out a name', category='danger' )
							return redirect(request.url)
						
						if not usefull_functions.allowed_files_ext(file_s.filename):
							flash(f'You cant Upload a file with extension {file_extension}', category='danger' )
							return redirect(request.url)
						
						else:
							#filename = current_user.surname + '12_4_2022_' +  secure_filename(file_s.filename)
							filename = current_user.surname+ '_' + usefull_functions.file_rename_date()+ '_' + key + file_ext(file_s.filename)
							
							#file_s.save(os.path.join(app.config['FILE_UPLOADS_LIQUIDATION'], file_s.filename))
							file_s.save(os.path.join(app.config['FILE_UPLOADS_LIQUIDATION'], filename))
							file_names_dict[key] = f'{filename}'
				
				print(file_names_dict)
				print(len(file_names_dict))

				if len(file_names_dict) ==0:
					#sql injection
					edit_liq.total_sales = form.total_sales.data
					edit_liq.bank_deposit = form.bank_deposit.data
					edit_liq.visa_transaction = form.visa_transaction.data
					edit_liq.pre_cancels = form.pre_cancels.data
					edit_liq.cancelled_tickets = form.cancelled_tickets.data
					edit_liq.remarks = form.remarks.data
					db.session.add(edit_liq)
					db.session.commit()
					flash(f'Liquidation DB_ID_No:{id} Updated Succesfully', category='info')
					return (redirect(url_for('daily_liquidation')))
				else:
					#delete previous uploaded files in file location
					if form.bank_dep_image.data:
						usefull_functions.file_deleter(form.bank_dep_image.data)
					
					if form.jcc_daily_batch_image.data:
						usefull_functions.file_deleter(form.jcc_daily_batch_image.data)
					
					if form.canceled_ticket_image.data:
						usefull_functions.file_deleter(form.canceled_ticket_image.data)
					
					edit_liq.total_sales = form.total_sales.data
					edit_liq.bank_deposit = form.bank_deposit.data
					edit_liq.visa_transaction = form.visa_transaction.data
					edit_liq.pre_cancels = form.pre_cancels.data
					edit_liq.cancelled_tickets = form.cancelled_tickets.data
					edit_liq.remarks = form.remarks.data
					
					if 'bank_dep_image'in file_names_dict.keys():
						edit_liq.bank_dep_image = file_names_dict['bank_dep_image']
					
					if 'jcc_daily_batch_image' in file_names_dict.keys():
						edit_liq.jcc_daily_batch_image =file_names_dict['jcc_daily_batch_image']
					
					if 'canceled_ticket_image' in file_names_dict.keys():
						edit_liq.canceled_ticket_image = file_names_dict['canceled_ticket_image']
					
					db.session.add(edit_liq)
					db.session.commit()
					flash(f'Liquidation DB_ID_No:{id} Updated Succesfully', category='info')
					return (redirect(url_for('daily_liquidation')))

		if form.errors != {}:
			print (form.errors)

		return render_template('edit_daily_liq.html', title = 'Edit Daily Liq.', form=form)

@app.route('/add_daily_liquidation', methods=['GET','POST'])
def add_daily_liquidation():
	form = Liquidation_Form()


	if request.method=="POST":		
		'''
		file size
		len(form.bank_dep_image.data.read())
		'''
		#usefull_functions.current_date()

		  
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
					print ('iam here')
					if form.cancelled_tickets_image.data:
						if not file_s.filename:
							flash(f'You cant Upload a file with out a name', category='danger' )
							return render_template('add_daily_liqui.html', title = 'Daily Liq.', form=form)
							# return redirect(request.url)
					
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


@app.route('/employees', methods=['GET','POST'])
def employees():
	deleteform = DeleteForm()
	disableform = DisableForm()
	enableform = EnableForm()
	if request.method=="POST":
		if request.form['submit_button'] == "Delete":
			#print(request.form.get('delete_emp'))
			#print(type(request.form.get('delete_emp')))
		
			delete_employee = Users.query.filter_by(id=int(request.form.get('delete_emp'))).delete()
			#print(delete_employee)
			db.session.commit()
			flash('Employee Deleted Succesfully', category='primary' )
		if request.form['submit_button'] == "Disable":
			print('yes is disabled')
			print(request.form.get('disable_emp'))
			dea_emp = db.session.query(Users).filter(Users.id==int(request.form.get('disable_emp'))).one()
			dea_emp.active = False
			db.session.commit()
			flash('Employee Deactivate Succesfully', category='primary' )
		if request.form['submit_button'] == "Enable":
			print('yes is enable')
			print(request.form.get('enable_emp'))
			ena_emp = db.session.query(Users).filter(Users.id==int(request.form.get('enable_emp'))).one()
			ena_emp.active = True
			db.session.commit()
			flash('Employee Enabled Succesfully', category='primary' )
			

	emp =  db.session.query(Users.id,Users.name,Users.surname,Users.email, 								Users.mobile_phone, Users.area_of_business, 
							Users.position, Users.active, Users.role, 		column_property(func.to_char(Users.date_of_birth, 'DD/MM/YYYY').label('date_of_birth')), 
							Users.annual_leave_total).filter(Users.active==True).order_by(Users.name)
	disabled_emp =  db.session.query(Users.id,Users.name,Users.surname,
									Users.email, Users.mobile_phone, Users.area_of_business, 
									Users.position, Users.active, Users.role, 	column_property(func.to_char(Users.date_of_birth, 'DD/MM/YYYY').label('date_of_birth')), 
									Users.annual_leave_total).filter(Users.active==False).order_by(Users.name)						

	return render_template('employee.html', emp = emp, disabled_emp= disabled_emp, title='Employees', deleteform=deleteform, disableform=disableform, enableform=enableform)




@app.route('/add_user', methods=['GET','POST'])
#@login_required
def add_user():		
	form = UsersForm()
	if form.validate_on_submit():

		user_role = ''
		if form.admin.data:
			user_role = user_role + 'Administrator'
		if form.rep.data:
			user_role = user_role + ', Representative'
		if form.rep_superv.data:
			user_role = user_role + ', Rep Supervisor'
		if form.escort.data:
			user_role = user_role + ', Escort'
		if form.bibliosha.data:
			user_role = user_role + ', Bibliosha'
		if form.off_rec.data:
			user_role = user_role + ', Office-Rec'	
		if form.off_hr.data:
			user_role = user_role + ', Office-HR'
		if form.off_exc.data:
			user_role = user_role + ', Office-Exc'
		if form.leaves.data:
			user_role = user_role + ', Leaves'	
		
		user_create=Users(name = form.name.data.strip(),
						  surname = form.surname.data.strip(),	
						  email = form.email.data.strip(),
						  password= form.password.data,
						  active = form.active.data,
						  area_of_business = form.area_of_business.data,
						  mobile_phone = form.mobile_phone.data,
						  date_of_birth = form.date_of_birth.data,
						  position = form.position.data,
						  registration_date = form.registration_date.data,
						  role = user_role.strip(',').strip(' ')

						  
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


@app.route('/edit_user/<int:id>', methods=['GET','POST'])
#@login_required
def edit_user(id):
	edit_user_db = db.session.query(Users).filter(Users.id==id).first()
	form = User_Edit_Form(formdata=request.form, obj=edit_user_db)
	
	if form.validate_on_submit():
		if form.name.data:
			edit_user_db.name = form.name.data
		if form.surname.data:
			edit_user_db.surname = form.surname.data
		if form.mobile_phone.data:
			edit_user_db.mobile_phone = form.mobile_phone.data
		if form.email.data:
			edit_user_db.email = form.email.data
		if form.date_of_birth.data:
			edit_user_db.date_of_birth = form.date_of_birth.data			
		if form.edit_password.data:
			edit_user_db.password = form.edit_password.data		
		if form.position.data:
			edit_user_db.position = form.position.data			
		if form.area_of_business.data:
			edit_user_db.area_of_business = form.area_of_business.data			
		
		user_role = ''
		if form.admin.data:
			user_role = user_role + 'Administrator'
		if form.rep.data:
			user_role = user_role + ', Representative'
		if form.rep_superv.data:
			user_role = user_role + ', Rep Supervisor'
		if form.escort.data:
			user_role = user_role + ', Escort'
		if form.bibliosha.data:
			user_role = user_role + ', Bibliosha'
		if form.off_rec.data:
			user_role = user_role + ', Office-Rec'	
		if form.off_hr.data:
			user_role = user_role + ', Office-HR'
		if form.off_exc.data:
			user_role = user_role + ', Office-Exc'
		if form.leaves.data:
			user_role = user_role + ', Leaves'
		
		if user_role:
			edit_user_db.role = user_role.strip(',').strip(' ')
		
		db.session.add(edit_user_db)
		db.session.commit()	
		flash(f'User:{edit_user_db.name} {edit_user_db.surname} Updated Succesfully', category='info')
		return (redirect(url_for('employees')))
	
	
	
	if form.errors != {}:
		for error_msg in form.errors.values():
			flash(f'Error Message : {error_msg[0]}', category='danger' )
		print('form errors')
	
	return render_template('edit_user.html',title = 'Edit User', form = form, roles = edit_user_db.role  )	

@app.route('/more_info_user/<int:id>', methods=['GET','POST'])
#@login_required
def more_info_user(id):
	asset_rent_form= AssetRentForm()

	if request.method=="POST":
		if request.form['submit_button'] =="Rent it":
			print('rent')
			rent_asset(asset_rent_form,request.form)
			flash(f'Asset Returned Succesfully', category='primary' )
		
			

	ownwed_daily_liqu = db.session.query(DailyLiquidation.id, DailyLiquidation.						total_sales, DailyLiquidation.bank_deposit, 								DailyLiquidation.visa_transaction, 
						DailyLiquidation.pre_cancels,DailyLiquidation.cancelled_tickets, DailyLiquidation.total_calculated_amount, 
						column_property(func.to_char(DailyLiquidation.date_time_actual, 'DD/MM/YYYY').label('date_time_actual')) ,
						#DailyLiquidation.date_time_actual,
						column_property(func.to_char(DailyLiquidation.date_liquidated,'DD/MM/YYYY').label('date_liquidated')),			
						DailyLiquidation.bank_dep_image, 
						DailyLiquidation.jcc_daily_batch_image,DailyLiquidation.canceled_ticket_image, DailyLiquidation.daily_liquidation_balance, DailyLiquidation.remarks,DailyLiquidation.confirm, Users.name,Users.surname, Users.position).filter(DailyLiquidation.owner ==id ).outerjoin(Users, Users.id==id).order_by(DailyLiquidation.id.desc()).all()
	
	user_is = db.session.query(Users.name, Users.surname, Users.registration_date).filter(Users.id==id, Users.active==True).one()

	owned_leaves = db.session.query(Leaves).filter( Leaves.owner == id ).all()
	
	
	#user_is = db.session.query(Users.name, Users.surname, Users.registration_date).filter(Users.id==id, Users.active==True).one()
	year = usefull_functions.current_date()[-4:]
	total_from_begining_annuals = count_annual_leaves(id)

	total_annual_current_year:dict = statistics_current_year(id)

	
	final_asset_owned = all_assets_rented(id)
	final_asset_owned.reverse()
	

	return render_template('more_info_user.html', title = 'User More Info', ownwed_daily_liqu = ownwed_daily_liqu, owned_daily_liq_exisatnce = len(ownwed_daily_liqu), name =user_is, total_from_begining_annuals = total_from_begining_annuals, year_stats = total_annual_current_year, year = year, leaves_existance = len(total_annual_current_year), final_asset_owned = final_asset_owned, asset_rent_form=asset_rent_form )




@app.route('/leaves', methods=['GET','POST'])
#@login_required
def leaves():
	
	deleteform = DeleteForm()	
	if request.method=="POST":
		if request.form['submit_button'] =="Delete":
			delete_leave = Leaves.query.filter_by(id=int(request.form.get('delete_leave'))).one()
			
			if delete_leave.reason=='Annual Leave' and delete_leave.confirm == 'true':
				
				emp = Users.query.filter(Users.id ==delete_leave.owner).one()
				emp.annual_leave_total = emp.annual_leave_total + delete_leave.total
			
			delete_leave = Leaves.query.filter_by(id=int(request.form.get('delete_leave'))).delete()			
			
			db.session.commit()
			flash('Leave Deleted Succesfully', category='primary' )

	if ('Administrator' in current_user.role) or ('Office-HR' in current_user.role):
		
		leaves_table =  db.session.query(Leaves.id,
										column_property(func.to_char(Leaves.from_, 'DD/MM/YYYY').label('from_')),
										column_property(func.to_char(Leaves.to_, 'DD/MM/YYYY').label('to_')),
										Leaves.total,
										Leaves.reason,
										Leaves.half,
										Leaves.docs,
										Leaves.remarks,	
										Leaves.confirm,
										Leaves.creator,
										Leaves.owner,
										Leaves.country,
										Users.name.label('fname'),
										Users.surname.label('surname')).outerjoin(Users, Users.id == Leaves.owner).order_by(Leaves.id.desc())
	
	else:

		leaves_table =  db.session.query(Leaves.id,
								column_property(func.to_char(Leaves.from_, 'DD/MM/YYYY').label('from_')),
								column_property(func.to_char(Leaves.to_, 'DD/MM/YYYY').label('to_')),
								Leaves.total,
								Leaves.reason,
								Leaves.half,
								Leaves.docs,
								Leaves.remarks,	
								Leaves.confirm,
								Leaves.country,
								Leaves.creator,
								Leaves.owner,							Users.name.label('fname'),
								Users.surname.label('surname')).outerjoin(Users, Users.id == Leaves.owner).filter(current_user.id == Leaves.owner).order_by(Leaves.id.desc())

	return render_template('Leaves/leaves.html', title = 'Leaves', leaves_table = leaves_table, deleteform = deleteform  )


@app.route('/leaves/add_leave', methods=['GET','POST'])
def add_leave():
	
	form = LeavesForm()
	if 'Administrator' in current_user.role or 'Office-HR' in current_user.role:
		#if the user is administrator or HR has to choose some employees names Excursions.days.contains(aday)
		emp =  db.session.query(Users.name,Users.surname).filter(Users.							active==True, Users.role.contains								('Leave')).order_by(Users.name)

		final_emp= [f'{item[0]} {item[1]}' for item in list(emp.all())]
		print(final_emp)
		form.employee.choices = final_emp
	else:
		form.employee.choices=[f'{current_user.name} {current_user.surname}']

	if request.method=="POST":
				
		if form.validate_on_submit():


			file_names_dict={}

			for key, value in request.files.items():
				# if the file is not empty	
				if not 'application/octet-stream' in value.content_type:
					
					file_s = request.files[key]
					print('this is my file')
					print(file_s)


					if not file_s.filename:
						flash(f'You cant Upload a file with out a name', category='danger' )
						return redirect(request.url)
					
					if not usefull_functions.allowed_files_ext(file_s.filename):
						flash(f'You cant Upload a file with out a name. Allowed File Names "PNG", "JPG", "JPEG" , "GIF", "PDF","DOC", "DOCX" ', category='danger' )
						return redirect(request.url)
					
					else:
						#filename = current_user.surname + '12_4_2022_' +  secure_filename(file_s.filename)
						filename = form.employee.data.split()[0] + '_' + form.employee.data.split()[1]  + '_' + str(form.from_.data) + '_' + str(form.to_.data) + '_' + form.reason.data + file_ext(file_s.filename)
						
						#file_s.save(os.path.join(app.config['FILE_UPLOADS_LIQUIDATION'], file_s.filename))
						file_s.save(os.path.join(app.config['FILE_UPLOADS_FOR_LEAVES'], filename))
						file_names_dict[key] = f'{filename}'
			
					print(file_names_dict)
					print(len(file_names_dict))
			
					print(file_names_dict)
					print(len(file_names_dict))
			

			if 'Administrator' in current_user.role or 'Office-HR' in current_user.role:
				search_val = form.employee.data.split()
							
				search_emp = db.session.query(Users.id).filter(Users.name==search_val[0]).filter(Users.surname == search_val[1])
				print(f'form total days {form.total_days_calc()}')
				
				if form.half_day.data == True:
					total_days = 0.5
				else:
					if form.reason.data == 'Annual Leave':
						total_days = float(form.total_days_calc()[0])
					else: 
						total_days = float(form.total_days_calc()[3])
					print(total_days)	
				
				if form.reason.data == 'Annual Leave':
					remarks = f'{form.remarks.data}, WeekendsDays: {form.total_days_calc()[1]}, Holiday days: {form.total_days_calc()[2]}'
				else:
					remarks = form.remarks.data			
				
				if len(file_names_dict)>0:


					leave_create = Leaves(
										from_ = form.from_.data,
										to_ = form.to_.data,	
										half = form.half_day.data,
										reason= form.reason.data,
										country = form.country.data,
										total = total_days,
										#remarks = form.remarks.data,
										docs = file_names_dict['docs'],
										creator = f'{current_user.name} {current_user.surname}',
										owner = search_emp.all()[0][0],
										remarks = remarks			  
										)
				else:
					leave_create = Leaves(
										from_ = form.from_.data,
										to_ = form.to_.data,	
										half = form.half_day.data,
										reason= form.reason.data,
										country = form.country.data,
										total = total_days,
										#remarks = form.remarks.data,	
										creator = f'{current_user.name} {current_user.surname}',
										owner = search_emp.all()[0][0],
										remarks = remarks	
										)	
			else:# if its not Admin or HR
				if form.half_day.data == True:
					total_days = 0.5
				else:
					if form.reason.data == 'Annual Leave':
						total_days = float(form.total_days_calc()[0])
					else: 
						total_days = float(form.total_days_calc()[3])
					print(total_days)	
				if form.reason.data == 'Annual Leave':
					remarks = f'{form.remarks.data}, WeekendsDays: {form.total_days_calc()[1]}, Holiday days: {form.total_days_calc()[2]}'
				else:
					remarks = form.remarks.data
				
				if len(file_names_dict)>0:		
					leave_create = Leaves(
										from_ = form.from_.data,
										to_ = form.to_.data,	
										half = form.half_day.data,
										reason= form.reason.data,
										country = form.country.data,
										total = total_days,
										#remarks = form.remarks.data,
										docs = file_names_dict['docs'],
										creator = f'{current_user.name} {current_user.surname}',
										owner = current_user.id	,
										remarks = remarks			  
										)
				else:
					leave_create = Leaves(
										from_ = form.from_.data,
										to_ = form.to_.data,	
										half = form.half_day.data,
										reason= form.reason.data,
										country = form.country.data,
										total = total_days,
										#remarks = form.remarks.data,	
										creator = f'{current_user.name} {current_user.surname}',
										owner = current_user.id	,
										remarks = remarks
										)	
														
			db.session.add(leave_create)
			db.session.commit()
			leave_history_create = LeavesHistory(leave_id = leave_hist_add(), 
										from_ = leave_create.from_,
										to_ = leave_create.to_,	
										half = leave_create.half,
										reason= leave_create.reason,
										country = leave_create.country,
										total = leave_create.total,	
										creator = leave_create.creator,
										owner = leave_create.owner	,		
										remarks = leave_create.remarks)
			try:
				db.session.add(leave_history_create)
				db.session.commit()
			except:
				pass
			flash(f'A Leave is Created Succesfully', category='primary' )
			return redirect(url_for('leaves'))

	
	if form.errors != {}:
		for error_msg in form.errors.values():
			flash(f'Error!!! {error_msg[0]}', category='danger' )
		
	return render_template('Leaves/add_leave.html', title='Add Leave', form=form)

@app.route('/leaves/edit/<int:id>', methods=['GET','POST'])
#@login_required
def leave_edit(id):
	print('Inside edit leave')
	leave_to_edit = db.session.query(Leaves).filter(Leaves.id==id).first()
	owner = db.session.query(Users).filter(Users.id==leave_to_edit.owner).first()
	print(owner.name, owner.surname)
	
	form = LeavesForm(formdata=request.form, obj = leave_to_edit)
	
	

	if 'Administrator' in current_user.role or 'Office-HR' in current_user.role:
		#if the user is administrator or HR has to choose some employees names
		emp =  db.session.query(Users.name,Users.surname).filter(Users.							active==True).filter(Users.id == 								leave_to_edit.owner).order_by(Users.name)
		print(emp.all())
		final_emp= [f'{item[0]} {item[1]}' for item in list(emp.all())]
		print(final_emp)
		form.employee.choices = final_emp
	else:
		form.employee.choices=[f'{current_user.name} {current_user.surname}']

	if request.method=="POST":
		print(f'test ::::: {request.files}')
		
		if form.validate_on_submit():
			
				
			print(request.files)
			file_names_dict={}

			for key, value in request.files.items():
				# if the file is not empty	
				if not 'application/octet-stream' in value.content_type:
					
					file_s = request.files[key]
					print('this is my file')
					print(file_s)


					if not file_s.filename:
						flash(f'You cant Upload a file with out a name', category='danger' )
						return redirect(request.url)
					
					if not usefull_functions.allowed_files_ext(file_s.filename):
						flash(f'You cant Upload a file with out a name. Allowed File Names "PNG", "JPG", "JPEG" , "GIF", "PDF","DOC", "DOCX" ', category='danger' )
						return redirect(request.url)
					
					else:
						#filename = current_user.surname + '12_4_2022_' +  secure_filename(file_s.filename)
						filename = owner.name + '_' + owner.surname + '_' + usefull_functions.file_rename_date()+ '_' + key + file_ext(file_s.filename)
						
						#file_s.save(os.path.join(app.config['FILE_UPLOADS_LIQUIDATION'], file_s.filename))
						file_s.save(os.path.join(app.config['FILE_UPLOADS_FOR_LEAVES'], filename))
						file_names_dict[key] = f'{filename}'
			
					print(file_names_dict)
					print(len(file_names_dict))
			
					print(file_names_dict)
					print(len(file_names_dict))

			if 'Administrator' in current_user.role or 'Office-HR' in current_user.role:
				if form.half_day.data == True:
					total_days = 0.5
				else:
					if form.reason.data == 'Annual Leave':
						total_days = float(form.total_days_calc()[0])
						if ((form.to_.data != leave_to_edit.to_) or (form.from_.data != leave_to_edit.from_ ) )and leave_to_edit.confirm =='true':
							upd_user = db.session.query(Users).filter(Users.id == leave_to_edit.owner).first()					
							print(leave_to_edit.total)
							upd_user.annual_leave_total = upd_user.annual_leave_total + leave_to_edit.total
							db.session.commit()

					else: 
						total_days = float(form.total_days_calc()[3])
					print(total_days)	
				
				if form.reason.data == 'Annual Leave':
					remarks = f'{form.remarks.data}, WeekendsDays: {form.total_days_calc()[1]}, Holiday days: {form.total_days_calc()[2]}'
				else:
					remarks = form.remarks.data


				
				search_val = form.employee.data.split()
				search_emp = db.session.query(Users.id).filter(Users.name==search_val[0]).filter(Users.surname == search_val[1])
				print(search_emp.all()[0][0])
				
				leave_to_edit.from_ = form.from_.data
				leave_to_edit.total =total_days
				leave_to_edit.to_ = form.to_.data
				leave_to_edit.half = form.half_day.data
				leave_to_edit.country = form.country.data
				leave_to_edit.reason = form.reason.data
				leave_to_edit.remarks = remarks
				if len(file_names_dict)>0:
					leave_to_edit.docs = file_names_dict['docs']
				leave_to_edit.creator = f'{current_user.name} {current_user.surname}'
				leave_to_edit.owner = search_emp.all()[0][0]
				if leave_to_edit.confirm =='true':		
					leave_confirm(id) 


			else: # if its normal user not admin or hr
				if form.half_day.data == True:
					total_days = 0.5
				else:
					if form.reason.data == 'Annual Leave':
						total_days = float(form.total_days_calc()[0])
					else: 
						total_days = float(form.total_days_calc()[3])
					print(total_days)	
				
				if form.reason.data == 'Annual Leave':
					remarks = f'{form.remarks.data}, WeekendsDays: {form.total_days_calc()[1]}, Holiday days: {form.total_days_calc()[2]}'
				else:
					remarks = form.remarks.data

				#execute query	
				leave_to_edit.from_ = form.from_.data
				leave_to_edit.to_ = form.to_.data
				leave_to_edit.half = form.half_day.data
				leave_to_edit.total = total_days
				leave_to_edit.country = form.country.data
				leave_to_edit.reason = form.reason.data
				leave_to_edit.remarks = remarks
				if len(file_names_dict)>0:
					leave_to_edit.docs = file_names_dict['docs']
				leave_to_edit.creator = f'{current_user.name} {current_user.surname}'
				leave_to_edit.owner = current_user.id			
				
					
			leave_hist_add = LeavesHistory(leave_id = id,
										from_ = leave_to_edit.from_,
										to_ = leave_to_edit.to_,
										half = leave_to_edit.half,
										total = leave_to_edit.total,
										reason = leave_to_edit.reason,
										remarks = leave_to_edit.remarks,
										docs = leave_to_edit.docs,
										owner = leave_to_edit.owner,
										country = leave_to_edit.country,
										creator = leave_to_edit.creator
			)
			db.session.add(leave_hist_add)
			db.session.commit()
			flash(f'A Leave is Edited Succesfully', category='primary' )
			return redirect(url_for('leaves'))
	if form.errors != {}:
		for error_msg in form.errors.values():
			flash(f'Error!!! {error_msg[0]}', category='danger' )
	form.id.data = id
	form.remarks.data=''
	if leave_to_edit.half == True:
		form.half_day.data = True
	return render_template('Leaves/leave_edit.html', form = form)

@app.route('/leaves/confirm/<int:id>', methods=['GET','POST'])
#@login_required
def leave_confirm(id):
	print(id)	
	leave_to_confirm = db.session.query(Leaves).filter(Leaves.id==id).one()
	con = leave_to_confirm.confirm
	print(con)
	if leave_to_confirm.half==False:
		leave_to_confirm.confirm = True
		
		if leave_to_confirm.reason == 'Annual Leave':
			user_to_update_leave_days = db.session.query(Users).filter(Users.id==leave_to_confirm.owner).one()
			
			print( user_to_update_leave_days)
			
			if  user_to_update_leave_days.annual_leave_total >= leave_to_confirm.total:
				user_to_update_leave_days.annual_leave_total = user_to_update_leave_days.annual_leave_total- leave_to_confirm.total
	else:
		leave_days = 0.5
		if leave_to_confirm.reason == 'Annual Leave':
			user_to_update_leave_days = db.session.query(Users).filter(Users.id==leave_to_confirm.owner).one()
			print('inside annual')
			print( user_to_update_leave_days)
			leave_to_confirm.confirm = True
			
			if  user_to_update_leave_days.annual_leave_total >= leave_days:
				user_to_update_leave_days.annual_leave_total = user_to_update_leave_days.annual_leave_total - leave_days

	leave_edit_his= LeavesHistory(leave_id = id,
								  	from_ = leave_to_confirm.from_,
									to_ = leave_to_confirm.to_,
								 	half = leave_to_confirm.half,
									total = leave_to_confirm.total,
									reason = leave_to_confirm.reason,
									confirm = True,
									remarks = leave_to_confirm.remarks,
									docs = leave_to_confirm.docs,
									owner = leave_to_confirm.owner,
									country = leave_to_confirm.country,
									creator = f'{current_user.name} {current_user.surname}')
	leave_to_confirm.creator = f'{current_user.name} {current_user.surname}'
	if con==False or con=="Pending Confirmation":
		db.session.add(leave_edit_his)
		flash(f'Leave Entrie Confirmed Succesfully', category='primary' )
	db.session.commit()
	
	return redirect(url_for('leaves'))	

@app.route('/leaves/decline/<int:id>', methods=['GET','POST'])
#@login_required
def leave_decline(id):	
	leave_to_decline = db.session.query(Leaves).filter(Leaves.id==id).one()
	leave_to_decline.confirm=False
	leave_to_decline.creator = f'{current_user.name} {current_user.surname}'
	
	leave_edit_his= LeavesHistory(leave_id = id,
								  	from_ = leave_to_decline.from_,
									to_ = leave_to_decline.to_,
								 	half = leave_to_decline.half,
									total = leave_to_decline.total,
									reason = leave_to_decline.reason,
									confirm = False,
									remarks = leave_to_decline.remarks,
									docs = leave_to_decline.docs,
									owner = leave_to_decline.owner,
									country = leave_to_decline.country,
									creator = f'{current_user.name} {current_user.surname}')
	
	db.session.add(leave_edit_his)	
	db.session.commit()
	flash(f'Leave Entrie Declined Succesfully', category='primary' )
	return redirect(url_for('leaves'))	

@app.route('/leaves/more/<int:id>', methods=['GET','POST'])
#@login_required
def leave_more(id):
	#aquery=db.session.query(Scheduler,Guides,Excursions).outerjoin(Scheduler, Guides.id==Scheduler.id_guides).outerjoin(Excursions, Excursions.id==Scheduler.id_excursion).

	leave_history = db.session.query(column_property(func.to_char								(LeavesHistory.from_, 'DD/MM/YYYY').label('from_')), 
										column_property(func.to_char(LeavesHistory.to_, 'DD/MM/YYYY').label('to_')), LeavesHistory.reason, LeavesHistory.docs, LeavesHistory.remarks, LeavesHistory.confirm, LeavesHistory.creator, LeavesHistory.country, LeavesHistory.total, LeavesHistory.log_time, Users.name, Users.surname).outerjoin(Users,LeavesHistory.owner == Users.id).filter(LeavesHistory.leave_id==id).order_by(LeavesHistory.id.desc()).all()

	
	return render_template('Leaves/leaves_more.html', table= leave_history)

@app.route('/leaves/leave_statistics/', methods=['GET','POST'])
def leave_statistics():
	'''route to present leaves statistics to the user mode only'''
	total_from_begining_annuals = count_annual_leaves(current_user.id)
	total_annual_current_year:dict = statistics_current_year(current_user.id)

	
	return render_template('Leaves/leave_statistics.html', name=f'{current_user.name} {current_user.surname}',total_from_begining_annuals = total_from_begining_annuals, year_stats = total_annual_current_year, leaves_existance = len(total_annual_current_year), title = 'Leave Statistics' )

#period_leave_search.html
@app.route('/leaves/period_leave_search/', methods=['GET','POST'])
def period_leave_search():
	form = SearchLeavePeriod()
	if request.method =='POST':

		search_period = usefull_functions.period_leave_days(form.from_.data, form.to_.data)
		
		leaves = db.session.query(Users.name, Users.surname, Leaves.from_, Leaves.to_).outerjoin(Leaves, Users.id==Leaves.owner).filter(or_(Leaves.confirm=='true', Leaves.confirm=='Pending Confirmation')).all()		
		table = []
		for item in leaves:			
			item_period = usefull_functions.period_leave_days(item.from_, item.to_)
			
		
			
			merged_days = [x for x in search_period if x in item_period]
			
			if merged_days:
				merged_days.sort()
				new_merged=[]
				for i in merged_days:
					d = usefull_functions.corect_date_format(i)

					new_merged.append(d)
				if not any(d['owner'] == f'{item.name} {item.surname}' for d in table):
					table.append({
						'owner':f'{item.name} {item.surname}',
						'leaves':new_merged
					})
				else:
					for t in table:
						if t['owner'] == f'{item.name} {item.surname}':
							t['leaves'] = t['leaves'] + new_merged 


		return render_template('Leaves/period_leave_search.html', form=form, table=table)



	return render_template('Leaves/period_leave_search.html', form=form)



@app.route('/public_holidays', methods=['GET','POST'])
#@login_required
def public_holidays():

	deleteform = DeleteForm()
	if request.method=="POST":
		if request.form['submit_button'] =="Delete":			
			delete_pu_hol = PublicHolidays.query.filter_by(id=int(request.form.get('delete_public_holiday'))).delete()
			#print(delete_employee)
			db.session.commit()
			flash('Public Holiday Deleted Succesfully', category='danger' )


	holidays =  db.session.query(PublicHolidays.id, column_property(func.to_char(PublicHolidays.date_of_holiday, 'DD/MM/YYYY').label('date_of_holiday')), PublicHolidays.country).order_by(PublicHolidays.country).order_by(PublicHolidays.date_of_holiday)
	
	return render_template('Public Holidays/public_holidays.html', holidays=holidays, title= 'Public Holidays', deleteform= deleteform)

@app.route('/add_public_holiday', methods=['GET','POST'])
#@login_required
def add_public_holiday():
	form = PublicHolidayForm()
	if request.method=="POST":
				
		if form.validate_on_submit():
			pub_create = PublicHolidays(
						date_of_holiday = form.date_of_holiday.data,
						country = form.country.data)
			db.session.add(pub_create)
			db.session.commit()
			flash(f'Public Holiday Created Succesfully', category='primary' )

	if form.errors != {}:
		for error_msg in form.errors.values():
			flash(f'Error!!! {error_msg[0]}', category='danger' )		
	
	return render_template('Public Holidays/add_public_holiday.html', form=form, title='Insert Public Holiday')


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



@app.route('/assets', methods=['GET', 'POST'])
def assets_page():
	delete_form = DeleteForm()	
	edit_asset_form = Assets_Edit_Form()
	edit_asset_form.category.choices =  asset_category_all()
	retire_asset_form= AssetRetireForm()
	asset_rent_form = AssetRentForm()

	#form.employee.choices = final_emp	
	#asset_rent_form.employee.choices = all_users_forms()
	
	
	if request.method=="POST":
		if request.form['submit_button'] =="Retire":
			print('retire' )
			print(request.form.get('retire_asset'))
			print(request.form.get('reg_date'))
			print(request.form.get('reason'))
			print(request.form.get('remarks'))
			
			
			asset_retire = AssetRetirement(
				serial_number = request.form.get('retire_asset'),
				date = request.form.get('reg_date'),
				reason =request.form.get('reason'),
				remarks =request.form.get('remarks')  )
			db.session.add(asset_retire)

			asset_retire = AssetRetirement.query.filter_by(serial_number = request.form.get('retire_asset')).first()
			print(asset_retire.id)
			asset_to_edit = db.session.query(Assets).filter(Assets.serial_number == asset_retire.serial_number).first()

			asset_to_edit.retire = asset_retire.id

			db.session.add(asset_to_edit)
			db.session.commit()
			flash(f'Asset Retired Succesfully', category='primary' )
			return redirect(url_for('assets_page'))
		
		if request.form['submit_button'] =="Delete":
			delete_asset = db.session.query(Assets.id,Assets.serial_number).filter_by(id=request.form.get('asset_delete'), ).first()
			print(delete_asset.id)
			print(delete_asset.serial_number)

			asset_deletion = Assets.query.filter_by(id=delete_asset.id).delete()

			#better do not delete retirement history. Maybe you need to check later
			#delete_asset_retire = AssetRetirement.query.filter_by(id=delete_asset.serial_number).delete()
			db.session.commit()

			flash(f'Asset Deleted Succesfully', category='primary' )
			return redirect(url_for('assets_page'))
		
		if request.form['submit_button'] =="Rent it":

			#print(asset_rent_form.given_out.data)
			#print(asset_rent_form.employee.data)
			owner =db.session.query(Users.id).filter(Users.name == request.form.get('employee').split()[0], Users.surname == request.form.get('employee').split()[1]).first()
			
			
			add_rented_history=AssetRentedHistory(asset=request.form.get('asset_rental_id'),given_out = request.form.get('given_out'),owner=owner[0],date = asset_rent_form.date.data,remarks = asset_rent_form.remarks.data)

			asset_update = db.session.query(Assets).filter(Assets.id == request.form.get('asset_rental_id')).first()
			
			asset_update.status=request.form.get('given_out')
			db.session.add(asset_update)
			
			db.session.add(add_rented_history)
			
			db.session.commit()
			flash(f'Asset Rented Succesfully', category='primary' )
			
			return redirect(url_for('assets_page'))

		if request.form['submit_button'] =="Save":
			'''Edit The Asset'''
			print('Asset Edit')
			
			if edit_asset_form.validate_on_submit():
				edit_asset = db.session.query(Assets.id,Assets.serial_number).filter_by(id=request.form.get('asset_edit'), ).first()
				print(edit_asset)
			
			if edit_asset_form.errors != {}:
				for error_msg in edit_asset_form.errors.values():
					flash(f'Error!!! {error_msg[0]}', category='danger' )	

			




	assets = db.session.query(Assets.id.label('assets_id'), Assets.serial_number,Assets.remarks, Assets.category, Assets.value, Assets.value,column_property(func.to_char(Assets.reg_date, 'YYYY-MM-DD').label('edit_date')), column_property(func.to_char(Assets.reg_date, 'DD/MM/YYYY').label('reg_date')),Assets.retire, AssetRentedHistory.id, AssetRentedHistory.asset, column_property(func.to_char(AssetRentedHistory.date, 'DD/MM/YYYY').label('date')), AssetRentedHistory.owner, AssetRentedHistory.given_out, Users.name, Users.surname).outerjoin(AssetRentedHistory, Assets.id ==AssetRentedHistory.asset).outerjoin(Users, AssetRentedHistory.owner == Users.id).order_by(AssetRentedHistory.id.desc()).all()

	
	final_asset = []
	assets_available=[]
	for asset in assets:		
		if asset.assets_id not in final_asset:
			final_asset.append(asset.assets_id)	
			assets_available.append(asset)


	#assets_available = db.session.query(Assets.id, Assets.category, Assets.value, Assets.remarks, Assets.retire, Assets.serial_number, Assets.status,column_property(func.to_char(Assets.reg_date, 'DD/MM/YYYY').label('reg_date'))).all()
	

	return render_template('Assets/assets.html', title='Assets', assets=assets_available, edit_asset_form=edit_asset_form, retire_asset_form=retire_asset_form, delete_form=delete_form, asset_rent_form = asset_rent_form, emp = all_users_forms(), category = asset_category_all()  )

@app.route('/add_asset', methods=['GET','POST'])
#@login_required
def add_asset():
	form = AssetsForm()
	asset_category= asset_category_all()
	form.category.choices = asset_category
	
	if form.validate_on_submit():
		asset_create= Assets(serial_number = form.serial_number.data,
		category=form.category.data,
		value = form.value.data,
		remarks = form.remarks.data,
		reg_date = form.reg_date.data)

		db.session.add(asset_create)
		db.session.commit()

		#print(user_create)
		flash(f'{form.category.data} - {form.serial_number.data} Created Succesfully', category='primary' )
		return redirect(url_for('assets_page'))
	
	if form.errors != {}:
		for error_msg in form.errors.values():
			flash(f'Error!!! {error_msg[0]}', category='danger' )		
		
	
	return render_template('Assets/add_asset.html', title = 'Add Asset', form = form)


@app.route('/edit_asset/<int:id>', methods=['GET','POST'])
#@login_required
def edit_asset(id):
	
	asset_to_edit = db.session.query(Assets).filter(Assets.id==id).first()
	form = Assets_Edit_Form(formdata=request.form, obj = asset_to_edit)
	form.category.choices = asset_category_all()
	
	if request.method=="POST":
		if form.validate_on_submit():
			print(form.category.data)
			asset_to_edit.serial_number = form.serial_number.data
			asset_to_edit.remarks = form.remarks.data
			asset_to_edit.reg_date= form.reg_date.data
			asset_to_edit.category = form.category.data
			
			db.session.add(asset_to_edit)
			db.session.commit()
			return redirect(url_for('assets_page'))
				

				
		if form.errors != {}:
			for error_msg in form.errors.values():
				flash(f'Error!!! {error_msg[0]}', category='danger' )



	return render_template('Assets/edit_asset.html', form=form)

@app.route('/more_info_asset/<int:id>', methods=['GET','POST'])
#@login_required
def more_info_asset(id):
	

	current_status = db.session.query(AssetRentedHistory.id,AssetRentedHistory.owner, AssetRentedHistory.asset, AssetRentedHistory.given_out, AssetRentedHistory.remarks, column_property(func.to_char(AssetRentedHistory.date, 'DD/MM/YYYY').label('rented_date')),Assets.serial_number,Assets.category, Users.name, Users.surname ).filter(AssetRentedHistory.asset==id).outerjoin(Assets, Assets.id ==AssetRentedHistory.asset).outerjoin(Users, AssetRentedHistory.owner == Users.id).order_by(AssetRentedHistory.id.desc()).first()

	rented_history = db.session.query(AssetRentedHistory.id,AssetRentedHistory.owner, AssetRentedHistory.asset, AssetRentedHistory.given_out, AssetRentedHistory.remarks, column_property(func.to_char(AssetRentedHistory.date, 'DD/MM/YYYY').label('rented_date')), Assets.serial_number,Assets.category, Users.name, Users.surname ).filter(AssetRentedHistory.asset==id).outerjoin(Assets, Assets.id ==AssetRentedHistory.asset).outerjoin(Users, AssetRentedHistory.owner == Users.id).order_by(AssetRentedHistory.id.desc()).all()


	
	return render_template("Assets/more_info_asset.html", title="Asset Info", rented_history = rented_history, current_status=current_status )

@app.route('/assetcategory', methods=['GET','POST'])
def assetcategory():
	form = DeleteForm()
	if request.method=="POST":
		if request.form['submit_button'] =="Delete":			
			delete_category = AssetCategory.query.filter_by(id=int(request.form.get('delete_category'))).delete()			
			db.session.commit()
			flash(f'Category  Deleted Succesfully', category='danger' )


	categories = AssetCategory.query.all()
	
	return render_template('AssetCategory/category.html', title="Asset Categories", categories = categories, form=form)

@app.route('/add_assetcategory', methods=['GET','POST'])
def add_assetcategory():
	form = AssetCategoryForm()
	categories = asset_category_all()
	

	if form.validate_on_submit():
		category_create = AssetCategory(category=form.category.data.capitalize())
		db.session.add(category_create)
		db.session.commit()
		flash(f'Category  - {form.category.data} -  Created Succesfully', category='primary' )
		return redirect(url_for('add_assetcategory'))
	
	if form.errors != {}:
		for error_msg in form.errors.values():
			flash(f'Error!!! {error_msg[0]}', category='danger' )
		print('form errors')
		return redirect(url_for('add_assetcategory'))

	return render_template('AssetCategory/addcategory.html', form=form, title="Add Asset Category", categories=categories)

@app.route('/assets_report', methods=['GET'])
#@login_required
def assets_report():
	all_assets = all_assets_rented()
	emp_has = np.unique([item['owner'] for item in all_assets])
	
	final=[]
	a=[]
	for emp in emp_has:
		a.append(emp)
		for asset in all_assets :
			if emp==asset['owner']:
				a.append(asset['asset'])
		final.append(a)	
		a=[]
	

	return render_template('Assets/assets_report.html', all_assets_table=final)


@app.route('/car_partners', methods=['GET','POST'])
#@login_required
def car_partners():
	form = DeleteForm()
	contractform = CarPartnerContractsForm()
	if request.method=="POST":
		if request.form['submit_button'] =="Delete":			
			delete_partner = Carpartner.query.filter_by(id=int(request.form.get('delete_partner'))).delete()			
			db.session.commit()
			flash(f'Car Rental Partner Deleted Succesfully', category='danger' )
			return redirect(url_for('car_partners'))
		if request.form['submit_button'] =="Save":
			file_name_details = request.form.get('contract_partner_name')+'_'+str(contractform.from_date.data)+'_'+ str(contractform.to_date.data) 
			print(file_name_details)
			
			file_name = contract_save(request, file_name_details)

			
			new_contract = CarPartnerContract(sign_date = contractform.sign_date.data, from_date = contractform.from_date.data, to_date = contractform.to_date.data, doc = file_name['doc'] , carpartner = request.form.get('contract_partner')  )
			
			db.session.add(new_contract)
			db.session.commit()
			
			flash(f'Contract Saved Succesfully', category='primary' )
			return redirect(url_for('car_partners'))
	partners = Carpartner.query.all()
	return render_template('CarPartners/car_partners.html', partners=partners, form=form, contractform =contractform)

@app.route('/car_partners_registration', methods=['GET','POST'])
#@login_required
def car_partner_add():
	form = CarPartnerForm()
	if request.method == "POST":
		if form.validate_on_submit():

			new_partner = Carpartner(company_name = form.name.data.capitalize(), phone = form.phone.data,email = form.email.data )

			db.session.add(new_partner)
			db.session.commit()

			flash(f'Partner  - {form.name.data} -  Created Succesfully', category='primary' )
			return redirect(url_for('car_partner_add'))
				

				
		if form.errors != {}:
			for error_msg in form.errors.values():
				flash(f'Error!!! {error_msg[0]}', category='danger' )
	partners = Carpartner.query.all()
	
	return render_template('CarPartners/add_car_partner.html', form=form, partners=partners)

@app.route('/car_partner_contracts/<int:id>', methods=['GET','POST'])
#@login_required
def car_partner_contracts(id):
	print(id)
	delete_form = DeleteForm()
	if request.method=="POST":
		if request.form['submit_button'] =="Delete":			
			delete_contract = CarPartnerContract.query.filter_by(id=int(request.form.get('contract_delete'))).delete()			
			db.session.commit()
			flash(f'Car Rental Contract Deleted Succesfully', category='danger' )
			return redirect(url_for('car_partners'))


	

	contracts = db.session.query(CarPartnerContract.id,column_property(func.to_char(CarPartnerContract.sign_date, 'DD/MM/YYYY').label('sign_date')),
	column_property(func.to_char(CarPartnerContract.from_date, 'DD/MM/YYYY').label('from_date')),
	column_property(func.to_char(CarPartnerContract.to_date, 'DD/MM/YYYY').label('to_date')), CarPartnerContract.doc, Carpartner.company_name).filter(CarPartnerContract.carpartner==id).join(Carpartner, Carpartner.id==CarPartnerContract.carpartner).order_by(CarPartnerContract.id.desc()).all()

	print(contracts)
	print(contracts[-1][-1])


	return render_template('CarPartners/car_partner_contract.html', title = "Partner Contract", delete_form = delete_form, contracts = contracts)

@app.route('/cars', methods=['GET','POST'])
#@login_required
def cars_page():
		page_title= 'Cars'
		return render_template('Cars/cars.html', title=page_title)


@app.route('/add_car', methods=['GET','POST'])
#@login_required
def add_car():
	form = CarForm()
	if request.method == "POST":
		
		if form.validate_on_submit():
			car_partner = db.session.query(Carpartner.id).filter_by(company_name = form.car_partner.data).first()

			newCar = Cars(reg_number=form.reg_number.data.upper(), category = form.category.data, model = form.model.data.capitalize(), engine_code = form.engine_code.data, vin = form.vin.data, cc = form.cc.data, remarks = form.remarks.data, carpartner= car_partner.id)
			
			db.session.add(newCar)
			db.session.commit()
			return redirect(url_for('cars_page'))
	return render_template('Cars/add_car.html', title='Add Car', form=form)


# @app.route('/car_partner_contract_add', methods=['GET','POST'])
# #@login_required
# def car_partner_contract_add():
# 	form = CarPartnerContractsForm()
# 	return render_template('car_partner_contract_add.html', form = form)



'''
string
int
float
path
uuid
'''

@app.route('/down-card-file/<string:file_name>', methods=['GET','POST'])
def down_card_file(file_name):
	try:
		return send_from_directory(app.config['FILE_UPLOADS_FOR_CARDS'],path=file_name, as_attachment=True)

	except FileNotFoundError:
		print('abort')
		abort(404)


@app.route('/down-file/<string:file_name>', methods=['GET','POST'])
def down_file(file_name):
	print(file_name)
	print(app.config['FILE_UPLOADS_LIQUIDATION'])
	try:
		return send_from_directory(app.config['FILE_UPLOADS_LIQUIDATION'],path=file_name, as_attachment=True)

	except FileNotFoundError:
		print('abort')
		abort(404)
	 

@app.route('/down-leave-file/<string:file_name>', methods=['GET','POST'])
def down_leave_file(file_name):
	print(file_name)
	print(app.config['FILE_UPLOADS_FOR_LEAVES'])
	try:
		return send_from_directory(app.config['FILE_UPLOADS_FOR_LEAVES'],path=file_name, as_attachment=True)

	except FileNotFoundError:
		print('abort')
		abort(404)


@app.route('/down-carcontract-file/<string:file_name>', methods=['GET','POST'])
def down_car_contract_file(file_name):
	print(file_name)
	print(app.config['FILE_UPLOADS_CAR_CONTRACTS'])
	try:
		return send_from_directory(app.config['FILE_UPLOADS_CAR_CONTRACTS'],path=file_name, as_attachment=True)

	except FileNotFoundError:
		print('abort')
		abort(404)
	 

@app.route('/testing', methods=['GET','POST'])
def test():
	emp = Users.query.all()
	return render_template('test_table_boot_code.html', emp = emp)


'''Make  404 error page custom'''

# def page_not_found(e):
#   return render_template('404.html'), 404

# app.register_error_handler(404, page_not_found)