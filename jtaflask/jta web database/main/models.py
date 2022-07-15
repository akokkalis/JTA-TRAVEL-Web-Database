#from email.policy import default
import datetime
from email.policy import default
from enum import unique
from tkinter import CASCADE
from main import db, login_manager, usefull_functions
from main import bcrypt
from flask_login import UserMixin
#from main import current_date, yesterday_date

'''
db.create_all()
db.drop_all()
db.session.rollback()
'''
@login_manager.user_loader
def load_user(users_id):
    return Users.query.get(int(users_id))



class Users(db.Model, UserMixin):    
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=20), nullable=False, unique=False)
    surname = db.Column(db.String(length=20), nullable=False, unique=False)   
    #username = db.Column(db.String(length=30), nullable=False, unique=True)
    email = db.Column(db.String(length=80), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=80), nullable=False)
    position = db.Column(db.String(length=20), nullable=False)
    role = db.Column(db.String(length=100), nullable=False)
    active = db.Column(db.Boolean, nullable = False, default=True)
    balance = db.Column(db.Float(), nullable=False, default=0.0)
    annual_leave_total = db.Column(db.Float(), nullable=False, default=21)
    mobile_phone = db.Column(db.String(length=15), nullable=False, unique=True)
    date_of_birth = db.Column(db.Date())
    area_of_business = db.Column(db.String(length=15), nullable=False)
    registration_date = db.Column(db.Date(), nullable=False, default = usefull_functions.current_date() )
    dai_liq = db.relationship('DailyLiquidation', backref='owned_user', lazy=True)
    
    leave = db.relationship('Leaves', backref='owned_user', lazy=True)
    card_returns = db.relationship('CardPaymentReturns', backref='owned_user', lazy=True)
    rented_history = db.relationship('AssetRentedHistory', backref='owned_user', lazy=True)
    rented_history =  db.relationship('CarRentedHistory', backref='user_owned_rental', lazy=True)
    

    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

class Leaves(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    from_ = db.Column(db.Date(), nullable=False)
    to_ = db.Column(db.Date(), nullable=False)
    half = db.Column(db.Boolean, nullable = False, default=False)
    reason =  db.Column(db.String(length=20), nullable=False)
    docs = db.Column(db.String(length=100), nullable=True)
    remarks = db.Column(db.String(length=300), nullable=True, unique=False)
    country = db.Column(db.String(length=300), nullable=False, unique=False,    default='CY')
    total = db.Column(db.Float(), nullable=False, default=0.0)
    confirm = db.Column(db.String(length=25), nullable = False, default='Pending Confirmation')
    creator = db.Column(db.String(length=20), nullable=False, unique=False)
    owner = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    leave_history = db.relationship('LeavesHistory', backref='owned_user', lazy=True)

class LeavesHistory(db.Model):
    id= db.Column(db.Integer(), primary_key=True)
    leave_id = db.Column(db.Integer(), db.ForeignKey('leaves.id', ondelete='CASCADE'))
    from_ = db.Column(db.Date(), nullable=False)
    to_ = db.Column(db.Date(), nullable=False)
    half = db.Column(db.Boolean, nullable = False, default=False)
    reason =  db.Column(db.String(length=20), nullable=False)
    docs = db.Column(db.String(length=100), nullable=True)
    remarks = db.Column(db.String(length=300), nullable=True, unique=False)
    confirm = db.Column(db.String(length=25), nullable = False, default='Pending Confirmation')
    country = db.Column(db.String(length=300), nullable=False, unique=False)
    total = db.Column(db.Float(), nullable=False, default=0.0)
    creator = db.Column(db.String(length=20), nullable=False, unique=False)
    log_time = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.now)
    owner = db.Column(db.Integer())





class DailyLiquidation(db.Model):    
    id = db.Column(db.Integer(), primary_key=True)
    total_sales = db.Column(db.Float(), nullable=False)
    bank_deposit = db.Column(db.Float(), nullable=False)
    visa_transaction = db.Column(db.Float(), nullable=False)
    pre_cancels = db.Column(db.Float(), nullable=False, default=0.0)
    cancelled_tickets = db.Column(db.String(length=300), nullable=False, unique=False)
    total_calculated_amount = db.Column(db.Float(), nullable=False)
    date_time_actual = db.Column(db.Date(), default= usefull_functions.current_date())
    date_liquidated = db.Column(db.Date(), default= usefull_functions.yesterday_date())
    bank_dep_image = db.Column(db.String(length=300), nullable=False)
    jcc_daily_batch_image = db.Column(db.String(length=300), nullable=False)
    canceled_ticket_image = db.Column(db.String(length=300), nullable=True)
    remarks = db.Column(db.String(length=300), nullable=True, unique=False)
    confirm = db.Column(db.Boolean, nullable = False, default=False)
    daily_liquidation_balance = db.Column(db.Float(), nullable=False)
    owner = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))

class PublicHolidays(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    date_of_holiday = db.Column(db.Date(), nullable=False)
    country = db.Column(db.String(length=300), nullable=False, unique=False,    default='CY')

class CardPaymentReturns(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    
    ticket_cancelled = db.Column(db.String(length=50), nullable=False, unique=True)
    
    excursion_name = db.Column(db.String(length=100), nullable=False, unique=False)
    
    booked_date = db.Column(db.Date(), nullable=False)

    clients_name =db.Column(db.String(length=60), nullable=False, unique=False)

    amount_returned = db.Column(db.Float(), nullable=False)
    
    batch_number = db.Column(db.String(length=15), nullable=False, unique=True)
    docs = db.Column(db.String(length=100))
    
    remarks = db.Column(db.String(length=300), nullable=True, unique=False)
    
    cancelled_date = db.Column(db.Date(), nullable=False )

    previous_week = db.Column(db.Boolean, nullable = False, default=False)
    
    owner = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))

# .create_all(checkfirst=True)

class AssetRetirement(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    remarks = db.Column(db.String(length=300), nullable=True, unique=False)
    date = db.Column(db.Date(), nullable=False )
    reason=db.Column(db.String(length=30), nullable=False, unique=False)
    serial_number = db.Column(db.String(50), nullable=False)
    asset = db.relationship('Assets', backref='retire_asset', lazy=True)

class Assets(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    serial_number = db.Column(db.String(50), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Float())
    remarks = db.Column(db.String(length=300), nullable=True, unique=False)
    reg_date= db.Column(db.DateTime(), nullable=False, default=datetime.datetime.now)
    status = db.Column(db.String(50))
    retire = db.Column(db.Integer(), db.ForeignKey(AssetRetirement.id, ondelete='CASCADE'))
    rented_history = db.relationship('AssetRentedHistory', backref='asset_hist', lazy=True)

class AssetCategory(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    category = db.Column(db.String(length=50), nullable=False, unique=True)

class AssetRentedHistory(db.Model):
    id =  db.Column(db.Integer(), primary_key=True)

    asset = db.Column(db.Integer(), db.ForeignKey('assets.id',ondelete='CASCADE'))

    owner = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))

    given_out = db.Column(db.String(20), nullable=False, unique=False )
    remarks = db.Column(db.String(length=300), nullable=True, unique=False)

    date = db.Column(db.Date(), nullable=False )

class Carpartner(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    company_name = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(length=50), nullable=False, unique=True)
    phone = db.Column(db.String(length=15), nullable=False, unique=True)
    cars = db.relationship('Cars', backref='cars', lazy=True)
    contracts = db.relationship('CarPartnerContract', backref='owned_contracts', lazy=True)


class CarPartnerContract(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    sign_date = db.Column(db.Date(), nullable=False )
    from_date = db.Column(db.Date(), nullable=False )
    to_date = db.Column(db.Date(), nullable=False )
    doc = db.Column(db.String(length=100), nullable=True)
    carpartner = db.Column(db.Integer(), db.ForeignKey(Carpartner.id,ondelete='CASCADE'))




class Cars(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    reg_number = db.Column(db.String(50), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=True)
    engine_code = db.Column(db.String(80), nullable=True)
    vin = db.Column(db.String(80), nullable=True, unique=True)
    cc = db.Column(db.String(80), nullable=True)
    remarks = db.Column(db.String(length=300), nullable=True, unique=False)
    carpartner = db.Column(db.Integer(), db.ForeignKey(Carpartner.id,ondelete='CASCADE'))
    rented_history =  db.relationship('CarRentedHistory', backref='car_owned_rental', lazy=True)

class CarRentedHistory(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    type = db.Column(db.String(10), nullable=False, unique=True)
    given_place = db.Column(db.String(10), nullable=False, unique=True)
    driver = db.Column(db.Integer(), db.ForeignKey(Users.id,ondelete='CASCADE'))
    car = db.Column(db.Integer(), db.ForeignKey(Cars.id,ondelete='CASCADE')) 

    