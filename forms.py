from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, DecimalField, DateField, validators, ValidationError
from wtforms.validators import DataRequired, Email, Length, Optional, InputRequired, NumberRange

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired(), Length(min=6, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        validators.DataRequired(),
        validators.Length(min=6),
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        validators.DataRequired(),
        validators.EqualTo('password', message='Passwords must match.')
    ])

class UserLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])

class AccountCreationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    account_type = SelectField('Account Type', choices=[('savings', 'Savings'), ('checking', 'Checking')], validators=[DataRequired()])
    balance = DecimalField('Balance', validators=[DataRequired(), NumberRange(min=0, message="Balance cannot be negative.")])

class BudgetCreationForm(FlaskForm):
    category = SelectField('Category', validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0, message="Amount cannot be negative.")])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])

    def validate_end_date(form, field):
        if field.data <= form.start_date.data:
            raise ValidationError("End date must be after start date.")

class TransactionForm(FlaskForm):
    type_choices = [('expense', 'Expense'), ('income', 'Income')]
    
    type = SelectField('Type', choices=type_choices, validators=[DataRequired()])
    category = SelectField('Category', choices=[], validators=[DataRequired()])
    description = StringField('Description', validators=[Optional()])
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0, message="Amount cannot be negative.")])
    date = DateField('Date', validators=[DataRequired()])
    account_id = SelectField('Account', coerce=int, validators=[InputRequired()], choices=[])

class GoalCreationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    target_amount = DecimalField('Target Amount', validators=[DataRequired(), NumberRange(min=0, message="Target amount cannot be negative.")])
