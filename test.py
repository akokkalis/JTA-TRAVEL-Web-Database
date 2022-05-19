from datetime import datetime
import datetime

def validate_date(adate):
    if isinstance(adate, (str)):
        #if its a string convert it to date value
        adate = datetime.datetime.strptime(adate, '%Y-%m-%d').date()
        
    if adate < datetime.date.today():
        
        return True
    else:
		
        return False

#print(validate_date('2022-05-19'))
from datetime import date
from dateutil.relativedelta import relativedelta
print(type(date.today()))
print(type(relativedelta(months=+3)))

six_months = date.today() - relativedelta(months=+3)
print(six_months)