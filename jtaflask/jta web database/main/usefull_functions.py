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





def leave_days(start, end, holidays=[]):
	from datetime import datetime, timedelta    
	end = end +  timedelta(days=1)	
	import numpy as np
	total_inc_hol = np.busday_count(start,end,
						weekmask=[1,1,1,1,1,0,0],
						)
	total = np.busday_count(start,end,
						weekmask=[1,1,1,1,1,0,0],
						holidays=holidays)
	weekends = np.busday_count(start, end, weekmask=[0,0,0,0,0,1,1])
	hol = total_inc_hol - total
	return [total, weekends, hol]






