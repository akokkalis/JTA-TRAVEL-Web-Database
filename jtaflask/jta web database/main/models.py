#from email.policy import default
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
    role = db.Column(db.String(length=15), nullable=False)
    active = db.Column(db.Boolean, nullable = False, default=True)
    balance = db.Column(db.Float(), nullable=False, default=0.0)    
    asset = db.relationship('Assets', backref='owned_user', lazy=True)

    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)


class Assets(db.Model):
   
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50))
    owner = db.Column(db.Integer(), db.ForeignKey('users.id'))


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
    
    owner = db.Column(db.Integer(), db.ForeignKey('users.id'))


