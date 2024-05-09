import os

from flask import Flask, render_template, request, flash, redirect, session, g, url_for
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from collections import defaultdict
import calendar
import plotly.graph_objs as go
from plotly.offline import plot
import plotly.express as px
import pandas as pd
import random
from flask_migrate import Migrate
from decimal import Decimal
from forms import RegistrationForm, UserLoginForm, AccountCreationForm, BudgetCreationForm, TransactionForm, GoalCreationForm
from models import db, connect_db, User, Accounts, Budgets, Transactions, Goals, Category, Expense
from sqlalchemy import extract, func




# Initialize your Flask app instance
app = Flask(__name__)

# App configuration
app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL', 'postgresql:///financemanager'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
CURR_USER_KEY = "user_id"
migrate = Migrate(app, db)
@app.before_first_request
def launch():
    upgrade()


# toolbar = DebugToolbarExtension(app)

# Connect the database to the Flask app
connect_db(app)


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

def random_value():
    # Return a random integer between 1000 and 5000 for example purposes
    return random.randint(1000, 5000)


##### get data from last n monts
    
def get_financial_data(user_id):

    year = datetime.now().year

    transactions = db.session.query(
        extract('month', Transactions.date).label('month'),
        Transactions.type,
        db.func.sum(Transactions.amount).label('total')
    ).filter(
        Transactions.user_id == user_id,
        extract('year', Transactions.date) == year
    ).group_by(
        extract('month', Transactions.date),
        Transactions.type
    ).all()

    income = [0] * 12 
    spending = [0] * 12

    for transaction in transactions:
        month_index = int(transaction.month) - 1
        if transaction.type == 'income':
            income[month_index] += transaction.total 
        else:
            spending[month_index] += transaction.total 


    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    return months, income, spending


# CHARTS
def create_budget_vs_spent_chart(user_id):
    user_budgets = Budgets.query.filter_by(user_id=user_id).all()

    categories = [budget.category.name for budget in user_budgets]
    budgeted_amounts = [budget.amount for budget in user_budgets]
    
    spent_amounts = [budget.spent if budget.spent else 0 for budget in user_budgets]

    remaining_budget = [max(0, b - s) for b, s in zip(budgeted_amounts, spent_amounts)]

    fig = go.Figure(data=[
        go.Pie(
            labels=categories, 
            values=remaining_budget, 
            hole=0.3,
            sort=False
        )
    ])

    fig.update_layout(
        title_text='Remaining Budget by Category',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    budget_chart_div = plot(fig, output_type='div', include_plotlyjs=False)
    
    return budget_chart_div

def create_account_balance_chart(user_id):
    user_accounts = Accounts.query.filter_by(user_id=user_id).all()
    plot_data = []

    if not user_accounts:
        return None

    for account in user_accounts:
        transactions = Transactions.query.filter_by(account_id=account.id).order_by(Transactions.date).all()
        if not transactions:
            continue

        dates = [transaction.date for transaction in transactions]
        balances = [0]
        balance = 0

        for transaction in transactions:
            balance += transaction.amount
            balances.append(balance)

        plot_data.append(go.Scatter(x=dates, y=balances, mode='lines+markers', name=account.name))

    if not plot_data:
        return None

    fig = go.Figure(data=plot_data)
    fig.update_layout(
        title='Account Balance Over Time',
        xaxis=dict(title='Date'),
        yaxis=dict(title='Balance'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    balance_chart_div = plot(fig, output_type='div', include_plotlyjs=False)
    return balance_chart_div

def generate_accounts_balance_chart(user_id):
    account_types_balances =db.session.query(
        Accounts.account_type,
        func.sum(Accounts.balance).label('total_balance')
    ).filter(Accounts.user_id == user_id).group_by(Accounts.account_type).all()

    account_types = [result.account_type for result in account_types_balances]
    balances = [float(result.total_balance) for result in account_types_balances]

    fig = go.Figure(data=[go.Pie(labels=account_types, values=balances, hole=0.3,
                                 textinfo='label+value',
                                 texttemplate='%{label}: $%{value:,}',
                                 insidetextorientation='radial'
                                 )])
    fig.update_layout(title='Accounts Balance Overview', paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)')
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div

def generate_financials_chart(user_id):
    monthly_financials = db.session.query(
        extract('month', Transactions.date).label('month'),
        extract('year', Transactions.date).label('year'),
        Transactions.type,
        func.sum(Transactions.amount).label('total_amount')
    ).filter(Transactions.user_id == user_id).group_by('month', 'year', Transactions.type).all()

    income_by_month = defaultdict(float)
    expenses_by_month = defaultdict(float)

    for financial in monthly_financials:
        month = int(financial.month)
        year = int(financial.year)
        month_year_key = f"{year}-{month:02d}"
        if financial.type == 'income':
            income_by_month[month_year_key] += float(financial.total_amount)
        elif financial.type == 'expense':
            expenses_by_month[month_year_key] += abs(float(financial.total_amount))

    all_months = sorted(set(income_by_month.keys()) | set(expenses_by_month.keys()))
    income_amounts = [income_by_month[month] for month in all_months]
    spending_amounts = [expenses_by_month[month] for month in all_months]

    fig = go.Figure(data=[
        go.Bar(name='Income', x=all_months, y=income_amounts),
        go.Bar(name='Spending', x=all_months, y=spending_amounts)
    ])
    fig.update_layout(barmode='group', title='Monthly Spending and Income', paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)')
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)

    return plot_div



##########homepages, login, logout, signup########################################
@app.route('/test-commit')
def test_commit():
    user = User.query.first()
    if user:
        user.last_login = datetime.utcnow()  # Assuming there's a last_login field
        db.session.commit()
        return "Commit successful"
    return "No user found"



@app.route('/')
def home():

    return render_template('homepage.html')

@app.route('/main-page')
def after_login():
    if g.user:
        accounts_plot_div = generate_accounts_balance_chart(g.user.id)
        financials_plot_div = generate_financials_chart(g.user.id)

        accounts = Accounts.query.filter_by(user_id=g.user.id).all()
        transactions = Transactions.query.filter_by(user_id=g.user.id).order_by(Transactions.date.desc()).all()
        budgets = Budgets.query.filter_by(user_id=g.user.id).all()
        goals = Goals.query.filter_by(user_id=g.user.id).all()
        print(session) 
        return render_template('main-page.html', accounts=accounts, transactions=transactions,
                               budgets=budgets, goals=goals, accounts_plot_div=accounts_plot_div,
                               financials_plot_div=financials_plot_div)
    else:
        return render_template('main-page.html', message="Please log in to view this page.") 

    
@app.route('/signup', methods=['GET', 'POST'])
def registration():
    """Signup Page"""
    form = RegistrationForm()

    if form.validate_on_submit():
        try:
           user = User.signup(
               first_name=form.first_name.data,
               last_name=form.last_name.data,
               username=form.username.data,
               email=form.email.data,
               password=form.password.data,
           ) 
           db.session.commit()
        except IntegrityError:
            flash("Username already taken", "danger")
            return render_template('signup.html', form=form)
        
        do_login(user)
        return redirect(url_for('after_login'))
    else:
        return render_template('signup.html', form=form)

    

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""

    form = UserLoginForm()

    if form.validate_on_submit():
        user = User.authentication(form.email.data,
                                   form.password.data)
        
        if user:
            do_login(user)
            flash("Welcome Back!", "success")
            return redirect(url_for('after_login'))
    
        flash("Invalid credentials.", "danger")
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash("You have successfully logged out.", "success")
    return redirect(url_for('home'))


#######adding account, transaction, setting goal, budget###########
@app.route('/account/add', methods=["GET", "POST"])
def addaccount():
    """Adding bank account"""
    if 'user_id' not in session:
        flash("You must be logged in to add an account.", "warning")
        return redirect(url_for('login'))
        print(session) 
    form = AccountCreationForm()

    if form.validate_on_submit():
        new_account = Accounts(name=form.name.data,
                               account_type=form.account_type.data,
                               balance=form.balance.data,
                               user_id=session['user_id'],
                               )
        print(session) 
        db.session.add(new_account)
        try:
            db.session.commit()
            flash("Account added successfully.", "success")
            return redirect(url_for('accounts'))
        except Exception as e:
            db.session.rollback()
            flash("Error adding account. Please try again.", "danger")
            #debugging
            print(e)

    return render_template('forms-templates/add-account.html', form=form)


@app.route('/transaction/add', methods=['GET', 'POST'])
def addtransaction():
    if 'user_id' not in session:
        flash("You must be logged in to add a transaction.", "warning")
        return redirect(url_for('login'))

    form = TransactionForm()
    form.account_id.choices = [(str(account.id), account.name) for account in Accounts.query.filter_by(user_id=session['user_id']).all()]
    form.category.choices = [(str(category.id), category.name) for category in Category.query.all()]
    
    if form.validate_on_submit():
        transaction_type = form.type.data
        category_id = int(form.category.data) if transaction_type == 'expense' else None
        account = Accounts.query.get(int(form.account_id.data))

        if not account:
            flash("Account not found.", "danger")
            return render_template('forms-templates/add-transaction.html', form=form)

        transaction_amount = Decimal(form.amount.data)

        if transaction_type == 'income':
            account.balance += transaction_amount
        else: 
            account.balance -= transaction_amount

        new_transaction = Transactions(
            type=transaction_type,
            description=form.description.data,
            amount=transaction_amount, 
            date=form.date.data,
            account_id=account.id,
            user_id=session['user_id'],
            category_id=category_id
        )
        db.session.add(new_transaction)


        if transaction_type == 'expense':
            active_budget = Budgets.query.filter(
                Budgets.category_id == category_id,
                Budgets.start_date <= new_transaction.date,
                Budgets.end_date >= new_transaction.date,
                Budgets.user_id == session['user_id']
            ).first()

            if active_budget:
               
                if active_budget.spent is None:
                    active_budget.spent = Decimal('0')
                active_budget.spent += transaction_amount

        db.session.commit()
        flash('Transaction added successfully!', 'success')
        return redirect(url_for('transactions'))

    return render_template('forms-templates/add-transaction.html', form=form)



        
@app.route('/budget/set', methods=["GET", "POST"])
def setbudget():
    if 'user_id' not in session:
        flash("You must be logged in to set a budget.", "warning")
        return redirect(url_for('login'))
    
    form = BudgetCreationForm()


    form.category.choices = [(str(c.id), c.name) for c in Category.query.order_by('name').all()]
    print("Category Choices:", form.category.choices)

    if form.validate_on_submit():
        category_id = int(form.category.data)
        category = Category.query.get(category_id)
    
        if category is None:
            flash(f"Category with ID '{category_id}' does not exist.", "danger")
            return redirect(url_for('setbudget'))
    
        new_budget = Budgets(
            category_name=category.name,
            amount=form.amount.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            user_id=session['user_id'],
            category_id=category_id 
        )

        db.session.add(new_budget)
        try:
            db.session.commit()
            flash("Budget added.", "success")
            return redirect(url_for('budgets'))
        except Exception as e:
            db.session.rollback()
            flash("Error setting budget.", "danger")
            print(e)


    return render_template('forms-templates/set-budget.html', form=form)



@app.route('/goal/set', methods=["GET", "POST"])
def setgoal():
    if 'user_id' not in session:
        flash("You must be logged in to set a budget.", "warning")
        return redirect(url_for('login'))
    
    form = GoalCreationForm()

    if form.validate_on_submit():
        new_goal = Goals(name=form.name.data,
                         target_amount=form.target_amount.data,
                         user_id=session['user_id'],
                         )
        db.session.add(new_goal)

        try:
            db.session.commit()
            flash("Goal added.", "success")
            return redirect(url_for('goals'))
        except Exception as e:
            db.session.rollback()
            flash("Error setting goal.", "danger")
            print(e)

    return render_template('forms-templates/set-goal.html', form=form)


#####goals, transactions, accounts, budgets page###################

@app.route('/account')
def accounts():
    if 'user_id' not in session:
        flash("You must be logged in to view accounts.", "warning")
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    balance_chart_div = create_account_balance_chart(user_id)
    user_accounts = Accounts.query.filter_by(user_id=user_id).all()

    return render_template('mainpages/accounts.html', accounts=user_accounts, balance_chart_div=balance_chart_div)



@app.route('/budget')
def budgets():
    if 'user_id' not in session:
        flash("You must be logged in to view accounts.", "warning")
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    budgets = Budgets.query.filter_by(user_id=user_id).all()

    budget_chart_div = create_budget_vs_spent_chart(session['user_id'])
    

    return render_template('mainpages/budgets.html', budget_chart_div=budget_chart_div, budgets=budgets)

@app.route('/goal')
def goals():
    if 'user_id' not in session:
        flash("You must be logged in to view accounts.", "warning")
        return redirect(url_for('login'))
    user_id = session['user_id']
    user_goals = Goals.query.filter_by(user_id=user_id).all()

    return render_template('mainpages/goals.html', goals=user_goals)

@app.route('/transaction')
def transactions():
    if 'user_id' not in session:
        flash("You must be logged in to view accounts.", "warning")
        return redirect(url_for('login'))
    user_id = session['user_id']
    user_transactions = Transactions.query.filter_by(user_id=user_id).all()

    return render_template('mainpages/transactions.html', transactions=user_transactions)


######Deleting goals, transactions, acccounts and budgets##############

@app.route('/account/delete/<int:account_id>', methods=['POST'])
def delete_account(account_id):
    if 'user_id' not in session:
        flash("You must be logged in to perform this action.", "warning")
        return redirect(url_for('login'))
    
    account_to_delete = Accounts.query.get_or_404(account_id)
    if account_to_delete.user_id != session['user_id']:
        flash("You do not have permission to delete this account.", "danger")
        return redirect(url_for('accounts'))

    db.session.delete(account_to_delete)
    db.session.commit()
    flash("Account deleted successfully.", "success")
    return redirect(url_for('accounts'))

@app.route('/goal/delete/<int:goal_id>', methods=["POST"])
def delete_goal(goal_id):
    if 'user_id' not in session:
        flash("You must be logged in to perform this action.", "warning")
        return redirect(url_for('login'))
    
    goal_to_delete = Goals.query.get_or_404(goal_id)
    if goal_to_delete.user_id != session['user_id']:
        flash("You do not have permission to delete this account.", "danger")
        return redirect(url_for('goals'))
    db.session.delete(goal_to_delete)
    db.session.commit()
    flash("Goal deleted successfully.", "success")
    return redirect(url_for('goals'))

@app.route('/budget/delete/<int:budget_id>', methods=["POST"])
def delete_budget(budget_id):
    if 'user_id' not in session:
        flash("You must be logged in to perform this action.", "warning")
        return redirect(url_for('login'))
    
    budget_to_delete = Budgets.query.get_or_404(budget_id)
    if budget_to_delete.user_id != session['user_id']:
        return redirect(url_for('budgets'))
    db.session.delete(budget_to_delete)
    db.session.commit()
    flash("budget deleted successfully.", "success")
    return redirect(url_for('budgets'))

@app.route('/transaction/delete/<int:transaction_id>', methods=["POST"])
def delete_transaction(transaction_id):
    if 'user_id' not in session:
        flash("Yu must be logged in to perform this action.", "warning")
        return redirect(url_for('login'))
    
    transaction_to_delete = Transactions.query.get_or_404(transaction_id)
    if transaction_to_delete.user_id != session['user_id']:
        return redirect(url_for('transactions'))
    db.session.delete(transaction_to_delete)
    db.session.commit()
    flash("Transaction deleted successfully.", "success")
    return redirect(url_for('transactions'))
    
