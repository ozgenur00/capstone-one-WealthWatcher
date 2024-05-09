from app import app, db
from models import User, Accounts, Budgets, Transactions, Goals, Category
from datetime import datetime
from flask_bcrypt import Bcrypt
import os

# Initialize Bcrypt outside of app context if not already initialized
bcrypt = Bcrypt(app)

def seed_database():
    with app.app_context():
        # Veritabanında herhangi bir kayıt olup olmadığını kontrol et
        if not db.session.query(User).first():
            print("Seeding data...")
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
        else:
            print("Database already contains data. No seed performed.")

if __name__ == '__main__':
    if os.getenv('FLASK_ENV') == 'development':
        seed_database()
    else:
        print('Seeding is skipped. Not in development environment.')
