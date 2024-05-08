from app import app, db
from models import User, Accounts, Budgets, Transactions, Goals, Category  # Import necessary models
from datetime import datetime
from flask_bcrypt import Bcrypt

# Initialize Bcrypt outside of app context if not already initialized
bcrypt = Bcrypt(app)

with app.app_context():
    # Drop all tables and recreate them
    db.drop_all()
    db.create_all()

    # Add categories to the database
    categories = [
        'Home and Utilities', 'Transportation', 'Groceries',
        'Health', 'Restaurants and Dining', 'Shopping and Entertainment',
        'Cash and Checks', 'Business Expenses', 'Education', 'Finance'
    ]
    
    for category_name in categories:
        category = Category(name=category_name)
        db.session.add(category)
        db.session.commit()  # Commit after adding all categories

    # Create a user and hash their password
    user_password = bcrypt.generate_password_hash('your_plain_text_password').decode('utf-8')
    user1 = User(
        first_name='John',
        last_name='Doe',
        username='johndoe',
        email='john@example.com',
        password=user_password
    )
    db.session.add(user1)
    db.session.commit()  # Commit to ensure user ID is generated

    # Create an account for the user
    account1 = Accounts(
        name='John Savings',
        account_type='savings',
        balance=1000.00,
        user_id=user1.id  # Use the user's ID
    )
    db.session.add(account1)
    db.session.commit()  # Commit to ensure account ID is generated

    # Create a transaction associated with the user and account
    transaction1 = Transactions(
        type='expense',
        description='Supermarket shopping',
        amount=100,  # Example amount
        date=datetime.now(),
        account_id=account1.id,  # Use the account's ID
        user_id=user1.id  # Use the user's ID
    )
    db.session.add(transaction1)
    db.session.commit()  # Final commit for the transaction

    print('Database seeded!')
