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


print(current_date())