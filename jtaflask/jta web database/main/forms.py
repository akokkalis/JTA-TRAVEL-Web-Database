from email import message
from turtle import position
from unicodedata import name
from wsgiref import validate
from flask_login import current_user
from flask_wtf import FlaskForm
from sqlalchemy import TEXT
from wtforms import StringField, PasswordField, SubmitField, IntegerField, EmailField, RadioField, SelectField, BooleanField, FloatField, FileField, TextAreaField, SelectMultipleField, DateField
from wtforms.validators import Length, Email, DataRequired, ValidationError, NumberRange, Regexp
from main.models import *
from main.usefull_functions import yesterday_date
from wtforms.widgets import TextArea
#from main.usefull_functions import current_date, yesterday_date


'''
class UsersForm(FlaskForm):

    name = StringField(label='First Name:')
    surname = StringField(label='Last Name:')
    username = StringField(label='username')
    email = EmailField(label='Email:')
    phone = IntegerField(label='Phone:')
    #password = PasswordField(label = 'password')
    password = StringField(label='password')
    job_title = StringField(label='Position:')
    area_of_working = StringField(label='Area Of Working:')
    test= RadioField(choices=['Lar', 'Lim'])
    
    test1= SelectField(label = 'test1', choices=['rep', 'escort'])
    submit = SubmitField(label = 'Add User')
'''

class UsersForm(FlaskForm):
    # validation function has to start with validate_ and then put exact column name
    def validate_email(self, email_to_check):
        user1 = Users.query.filter_by(email = email_to_check.data).first()
        if user1:
            raise ValidationError('Email Already Exists in Database. Please Enter a Different Email')
    def validate_mobile_phone(self, mobile_phone_to_check):
        #user1 = Users.query.filter_by(mobile_phone = mobile_phone_to_check.data).filter_by(active=True).first()
        user1 = Users.query.filter_by(mobile_phone = mobile_phone_to_check.data,active=True).first()        
        if user1:
            raise ValidationError('Mobile Phone Already Exists in Database. Please Enter a Different Mobile Phone')
    

    name = StringField(label='First Name:', validators=[Length(min=2, max=15),DataRequired()])
    surname = StringField(label='Last Name:', validators=[Length(min=2, max=15),DataRequired()])
    email = EmailField(label='Email:', validators=[Email(),DataRequired()])
    mobile_phone = StringField(label = 'Mobile Number', validators=[Regexp('^\d{8}$',message = 'Telephone must contains only digits, No letters and has to be minimum 8 length'),Length(min=8), DataRequired()])
    date_of_birth = DateField(label='Date of Birth:')
    area_of_business = SelectField (label = 'Working Area', choices=['LARNACA', 'AYIA NAPA', 'PROTARAS', 'PAPHOS', 'LIMASOL', 'OFFICE'])
    password = PasswordField( label='password',validators=[Length(min=5),DataRequired()] )
    admin = BooleanField('Administrator:')
    rep = BooleanField('Representative:')
    rep_superv = BooleanField('Rep Supervisor:')
    escort = BooleanField('Escort:')
    bibliosha = BooleanField('Bibliosha:')
    off_rec = BooleanField('Office-Rec:')
    off_hr = BooleanField('Office-HR:')
    off_exc = BooleanField('Office-Exc:')
    leaves = BooleanField('Leaves:')
    position = SelectField(label='Position:', choices=['Administrator', 'Representative', 'Rep Supervisor','Escort', 'Bibliosha','Airport', 'Office-Staff' ])
    #role= SelectMultipleField(label = 'Role', choices=['Administrator', 'Office Rec Staff', 'Representative', 'HR'])
    active = BooleanField(label = 'Active: ')#, choices=[True, False])

class User_Edit_Form(FlaskForm):
    
    def validate_email(self, email_to_check):
               
        user1 = Users.query.filter_by(email = email_to_check.data).first()
        
        if user1:
            
            if user1.id != self.id.data:         
                print('inside user1',f'{user1.id}')
                raise ValidationError('Email Already Belongs To Another User in Database. Please Use a Different Email')
    
    def validate_mobile_phone(self, mobile_phone_check):
        '''
        Validate mobile phone only for active users. We can have same number but for inactive users.        '''
               
        user1 = Users.query.filter_by(mobile_phone = mobile_phone_check.data).first()
        
        if user1:            
            if (user1.id != self.id.data) and (user1.active==True):                
                raise ValidationError('Mobile Number Already Belongs To Another User in Database. Please Use a Different Mobile Number')    



    id = IntegerField()
    name = StringField(label='First Name:', validators=[Length(min=2, max=15),DataRequired()])
    surname = StringField(label='Last Name:', validators=[Length(min=2, max=15),DataRequired()])
    email = EmailField(label='Email:', validators=[Email(),DataRequired()])
    mobile_phone = StringField(label = 'Mobile Number', validators=[Regexp('^\d{8}$',message = 'Telephone must contains only digits, No letters and has to be minimum 8 length'),Length(min=8), DataRequired()])
    date_of_birth = DateField(label='Date of Birth:')

    area_of_business = SelectField (label = 'Working Area', choices=['LARNACA', 'AYIA NAPA', 'PROTARAS', 'PAPHOS', 'LIMASOL', 'OFFICE'])
    edit_password = PasswordField( label='New Passwod:' )
    admin = BooleanField('Administrator:')
    rep = BooleanField('Representative:')
    rep_superv = BooleanField('Rep Supervisor:')
    escort = BooleanField('Escort:')
    bibliosha = BooleanField('Bibliosha:')
    off_rec = BooleanField('Office-Rec:')
    off_hr = BooleanField('Office-HR:')
    off_exc = BooleanField('Office-Exc:')
    leaves = BooleanField('Leaves:')
    position = SelectField(label='Position:', choices=['Administrator', 'Representative', 'Rep Supervisor','Escort', 'Bibliosha','Airport', 'Office-Staff' ])
    #role= SelectMultipleField(label = 'Role', choices=['Administrator', 'Office Rec Staff', 'Representative', 'HR'])
    active = BooleanField(label = 'Active: ')#, choices=[True, False])
    



class LoginForm(FlaskForm):
    email = EmailField(label='Email:', validators=[Email(),DataRequired()])
    password = PasswordField( label='Password:', validators=[DataRequired()] )


class DeleteForm(FlaskForm):
    submit = SubmitField(label = 'Delete', name='submit_button')

class DisableForm(FlaskForm):
    submit = SubmitField(label = 'Disable', name='submit_button')

class EnableForm(FlaskForm):
    submit = SubmitField(label = 'Enable', name='submit_button')

class AssetsForm(FlaskForm):
    # validation function has to start with validate_ and then put exact column name
    def validate_name(self, name):
        assets_find = Assets.query.filter_by(name = name.data).first()
        if assets_find:
            raise ValidationError('This asset  Already Exists in Database!')
    

    name = StringField(label='Asset Name:', validators=[Length(min=2, max=50),DataRequired()])
    submit = SubmitField(label = 'Save')


class Assets_Edit_Form(FlaskForm):
    emp = Users.query.all()
   
    name = StringField(label='Asset Name:', default='sdfsdfdsfdsssfdfsd')
    owner = SelectField(label = 'Owner', choices=[f'{item.name} {item.surname}' for item in emp])
    submit = SubmitField(label = 'Save')


class Liquidation_Form(FlaskForm):
    yesterday = usefull_functions.yesterday_date()
    
    total_sales = FloatField(label=f'Sales On Date {yesterday}', validators=[DataRequired()])
    
    bank_deposit = FloatField(label=f'Bank Deposit Amount For Date {yesterday}', validators=[DataRequired()])

    visa_amount = FloatField(label=f'Visa Total Amount For Date {yesterday}', validators=[DataRequired()])

    precancels = FloatField(label=f'Previous Days Cancellations ', validators=[DataRequired()])

    canceled_tickets = TextAreaField(label = 'Canceled Tickets', default='')
    
    bank_dep_image = FileField(label = f'Bank Deposit Picture for{yesterday}',validators=[DataRequired()])
    
    jcc_daily_image = FileField(label = f'JCC Batch Report for {yesterday}',validators=[DataRequired()])
    
    cancelled_tickets_image = FileField(label = f'Excursion Cancelled Tickets Made {yesterday}')

    remarks = TextAreaField(label=f'Comments For Your {yesterday} Sales', widget=TextArea())
    submit = SubmitField(label = 'Save')

class Liq_Edit_Form(FlaskForm):
    
    
    total_sales = FloatField(label=f'Total Sales', validators=[DataRequired()])
    
    bank_deposit = FloatField(label=f'Bank Deposit Amount', validators=[DataRequired()])

    visa_transaction = FloatField(label=f'Visa Total Amount', validators=[DataRequired()])

    pre_cancels = FloatField(label=f'Previous Days Cancellations ')

    cancelled_tickets = TextAreaField(label = 'Canceled Tickets')
    
    bank_dep_image = FileField(label = f'Bank Deposit File')
    
    jcc_daily_batch_image = FileField(label = f'JCC Batch Report')
    
    canceled_ticket_image = FileField(label = f'Excursion Cancelled Tickets')

    remarks = TextAreaField(label=f'Remarks', widget=TextArea())
    submit = SubmitField(label = 'Save')

class LeavesForm(FlaskForm):
    
    def validate_from_(self, from_):
        from datetime import date
        from dateutil.relativedelta import relativedelta
        self.existance()
        three_months = date.today() - relativedelta(months=+3)
        
        if three_months > self.from_.data:
            raise ValidationError('"From Date" Has To Be Earlier than 3 months') 
       
        
        if from_.data > self.to_.data:
            raise ValidationError('"From Date" Has To Be Earlier than "To Date"')
        if (self.half_day.data == True) and (from_.data!=self.to_.data): 
            raise ValidationError('Because You Select Half Day, Dates "From" And "To" Must Be Equal  ')

    def validate_remarks(self, remarks): 
        '''
        Validate Other Reason has to put some remarks
        '''
        
        if self.reason.data == 'Other' and len(self.remarks.data) < 5:          
            raise ValidationError('Because You Specify Reason Of Leave "Other" You Need To Explain For What is your Leave Request On Remarks Field.') 
    
    def validate_reason(self, reason):
        if self.reason.data == 'Annual Leave':
            print('this is my reason')
            name = self.employee.data.split()[0]
            surname = self.employee.data.split()[1]
            

            
            print(self.half_day.data)
            
            total_days = self.total_days_calc()[0]
            
            
            
            
            user_to_check = db.session.query(Users.name, Users.surname, Users.annual_leave_total, db.func.sum(Leaves.total)).filter(Users.name==name, Users.surname == surname, Leaves.reason=='Annual Leave', Leaves.confirm != 'false').outerjoin(Leaves, Leaves.owner==Users.id).group_by(Users.id, Leaves.owner).all()           
            
            print(f'user is {user_to_check}'  )
            


            try_to_insert = self.to_.data - self.from_.data 
            
            if user_to_check:
                if total_days + user_to_check[0][3] > user_to_check[0][2]:
                    raise ValidationError(f'You allowed {user_to_check[0][2] - user_to_check[0][3]} days to request as annual leave and you request {total_days} days ') 
            else: 
                #the user first time tries to send leave request
                user_to_check = db.session.query(Users).filter(Users.name==name).filter(Users.surname==surname).one()
                print(f'first {user_to_check.annual_leave_total} ')
               
                if total_days > user_to_check.annual_leave_total: 
                    raise ValidationError(f'You allowed {user_to_check.annual_leave_total} days to request as annual leave and you request {total_days} days ')  
    
    def existance(self):        
        import datetime
        # take the employee name and split so we can make a query
        search_val = self.employee.data.split()
        #query the database and give the user object with al of his attributes	
        search_emp = db.session.query(Users.id).filter(Users.name==search_val[0]).filter(Users.surname == search_val[1]).one()
        print(search_emp[0])
		#Query leave period and give me all users leaves entries that he has bigger to	
        leaves_period = db.session.query(Leaves).filter(Leaves.owner==search_emp[0], Leaves.to_ >= self.from_.data).order_by(Leaves.id.desc())
 	
        # for loop to compare the dates 
        for item in leaves_period:
            date_generated_db = [str(item.from_ + datetime.timedelta(days=x)) for x in range(0, (item.to_ - item.from_ ).days +1 )]

            print(date_generated_db)
            

            date_range_form = [ str(self.from_.data + datetime.timedelta(days=x)) for x in range(0, (self.to_.data  - self.from_.data ).days +1 )]
            print('List generated according form request')
            print(date_range_form)

            same_dates = set(date_range_form).intersection(date_generated_db)
            if len(same_dates) != 0:
                raise ValidationError(f'You are Trying to request {self.reason.data} leave, but you already have an entrie leave for that date period in database - {sorted(same_dates)} - for a reason {item.reason}. Please delete that existing entrie and try again.')  

    def total_days_calc(self):
        pu_h = db.session.query(db.func.to_char(PublicHolidays.date_of_holiday,'yyyy-mm-dd')).filter(PublicHolidays.country == self.country.data).all()
        
        holidays = [item[0] for item in pu_h]            

        total_days = usefull_functions.leave_days(self.from_.data, self.to_.data, holidays)
        return(total_days)

        
        

    
    employee = SelectField(label='Employee Name:', coerce=str)
    from_ = DateField(label='From:',validators=[DataRequired()])
    to_ = DateField(label='To:',validators=[DataRequired()])
    country= SelectField(label='Public Holiday Country:', choices=['CY', 'RU'], default='CY')
    half_day = BooleanField('Half Day:')
    reason = SelectField(label='Reason Of Leave:', choices=['Annual Leave','Military', 'Sick - Leave', 'UnPaid', 'Working-Off','Working-On', 'Public-On', 'Public-Off', 'Other' ], default='Annual Leave')
    docs = FileField(label = 'Document For Leave:')
    remarks = TextAreaField(label=f'Remarks:', widget=TextArea())
    submit = SubmitField(label = 'Save')


class PublicHolidayForm(FlaskForm):

    def validate_date_of_holiday(self,date_of_holiday):
        record = db.session.query(PublicHolidays).filter(PublicHolidays.date_of_holiday == self.date_of_holiday.data, 
        PublicHolidays.country==self.country.data).all()
        print(len(record))
        if len(record)!=0:
            raise ValidationError(f'Date {self.date_of_holiday.data} for Country {self.country.data} already exists. ')

    country = SelectField(label='Country:', choices=['CY', 'RU'])
    date_of_holiday =  DateField(label='Date:',validators=[DataRequired()])
    submit = SubmitField(label = 'Save')