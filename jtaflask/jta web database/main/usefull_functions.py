from main import app
import os
def current_date()-> str:
	'''
	Returns Current Date
	'''
	from datetime import date
	return date.today().strftime("%m/%d/%Y")

def yesterday_date()->str:
	'''
	Returns Yesterday Date
	'''
	from datetime import date, timedelta	
	return ((date.today()- timedelta(days=1)).strftime("%m/%d/%Y"))

def allowed_files_ext(filename):
	if not '.' in filename:
		return False

	ext = filename.rsplit('.', 1)[1]
	print(ext)
	if ext.upper() in app.config['ALLOWED_FILE_EXTENSIONS']:
		return True
	else:
		return False

def file_rename_date():
	from datetime import date, timedelta	
	return ((date.today()- timedelta(days=1)).strftime("%d_%m_%Y"))
	


def file_ext(filename):	
	if not '.' in filename:
		return False

	ext = filename.rsplit('.', 1)[1]
	return f'.{ext}'

def file_deleter(filename):
	os.remove(os.path.join(app.config['FILE_UPLOADS_LIQUIDATION'],filename))





def weekend_exclude():
	''' Check if we need that'''
	import numpy as np
	import datetime as dt

	start = dt.date( 2022, 5, 23 )
	end = dt.date( 2022, 6, 5 )

	days = np.busday_count( start, end )+1
	return days

def range_dates_between(item, start_d, end_d ):
	import datetime
	print(f'item id {item.id}'  )


	date_generated_db = [str(item.from_ + datetime.timedelta(days=x)) for x in range(0, (item.to_ - item.from_ ).days +1 )]
	print('list db')
	print('List generated according db object')
	print(date_generated_db)
	

	date_range_form = [ str(start_d + datetime.timedelta(days=x)) for x in range(0, (end_d  - start_d ).days +1 )]
	print('List generated according form request')
	print(date_range_form)


	same_dates = set(date_range_form).intersection(date_generated_db)
	print('Comparison List Result')
	print(same_dates)
	
	return True


#print(range_dates_between())

