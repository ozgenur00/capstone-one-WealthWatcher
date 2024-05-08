# tests/test_expense.py
import unittest
from datetime import datetime
from flask import Flask
from models import db, connect_db, User, Category, Budgets, Expense

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///wealthwatcher_test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TESTING'] = True

with app.app_context():
    connect_db(app)
    db.create_all()

class ExpenseModelTestCase(unittest.TestCase):
    def setUp(self):
        """Create test client and add sample data."""
        with app.app_context():
            db.drop_all()
            db.create_all()
            
            self.client = app.test_client()

            # Creating a user
            user = User(first_name="Test", last_name="User", username="testuser", email="test@example.com", password="password")
            db.session.add(user)
            db.session.commit()

            # Creating a category
            category = Category(name="Food")
            db.session.add(category)
            db.session.commit()

            # Creating a budget
            budget = Budgets(category_name="Food", amount=1500, start_date=datetime.now(), end_date=datetime.now(), user_id=user.id, category_id=category.id)
            db.session.add(budget)
            db.session.commit()

            # Creating an expense
            expense = Expense(amount=200, description="Groceries", date=datetime.now(), category_id=category.id, user_id=user.id, budget_id=budget.id)
            db.session.add(expense)
            db.session.commit()

            self.expense_id = expense.id

    def tearDown(self):
        """Clean up any fouled transaction."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_expense_creation(self):
        """Test the expense creation and its properties."""
        with app.app_context():
            expense = Expense.query.get(self.expense_id)
            self.assertEqual(expense.amount, 200)
            self.assertEqual(expense.description, "Groceries")
            self.assertEqual(expense.user_id, 1)
            self.assertEqual(expense.category_id, 1)
            self.assertEqual(expense.budget_id, 1)

    def test_expense_relationships(self):
        """Test the relationships associated with the Expense model."""
        with app.app_context():
            expense = Expense.query.get(self.expense_id)
            self.assertIsNotNone(expense.user)
            self.assertEqual(expense.user.username, 'testuser')
            self.assertIsNotNone(expense.category)
            self.assertEqual(expense.category.name, 'Food')
            self.assertIsNotNone(expense.budget)
            self.assertEqual(expense.budget.amount, 1500)

if __name__ == '__main__':
    unittest.main()
