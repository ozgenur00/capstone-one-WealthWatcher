
from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship


bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """
    db.app = app
    db.init_app(app)


class Expense(db.Model):
    """Expense model"""

    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False, default=lambda: datetime.today())

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    category = db.relationship('Category', backref='expenses')

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='expenses')

    budget_id = db.Column(db.Integer, db.ForeignKey('budgets.id'), nullable=False)
    budget = db.relationship('Budgets', backref='expenses')

    def __repr__(self):
        return f"<Expense id={self.id}, amount={self.amount}, description={self.description}, date={self.date}>"


class Category(db.Model):
    """Category model"""

    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)


class User(db.Model):
    """Users model"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    #define one-to-many relationship with accounts
    accounts = db.relationship('Accounts', backref='user', lazy=True)
    #define one-to-many relationship with budgets
    budgets = db.relationship('Budgets', backref='user', lazy=True)
    #define one-to-many relationship with goals
    goals = db.relationship('Goals', backref='user', lazy=True)

    @classmethod
    def authentication(cls, email, password):
        user = cls.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            return user
        else:
            return None
        

    @classmethod
    def signup(cls, first_name, last_name, username, email, password):
        hashed_pwd = generate_password_hash(password)
        user = cls(first_name=first_name, last_name=last_name, username=username, email=email, password=hashed_pwd)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None
        return user


class Accounts(db.Model):
    """Accounts model"""

    __tablename__ = 'accounts'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.Text)
    account_type = db.Column(db.Text)
    balance = db.Column(db.Numeric(10,2))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    #define many-to-one relationship with users
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    #define one-to-many relationship with transactions
    transactions = db.relationship('Transactions', backref='account', lazy=True)



class Budgets(db.Model):
    """Budgets model"""

    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric(10,2), nullable=False)

    spent = db.Column(db.Numeric(10,2), nullable=True)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    category = db.relationship('Category', backref='budgets')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"<Budget id={self.id}, category_name={self.category_name}, amount={self.amount}, start_date={self.start_date}, end_date={self.end_date}, created_at={self.created_at}>"


class Transactions(db.Model):
    """Transactions model"""

    __tablename__ = 'transactions'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    type = db.Column(db.Text)
    description = db.Column(db.Text)
    amount = db.Column(db.Numeric(10,2))
    date = db.Column(db.Date)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    category = db.relationship('Category', backref='transactions')

    #define many-to-one relationshio with accounts
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  
    user = db.relationship('User', backref='transactions')

class Goals(db.Model):
    """Goals model"""

    __tablename__ = 'goals'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.Text)
    target_amount = db.Column(db.Numeric(10,2))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    #define many-to-one relationship with users
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)