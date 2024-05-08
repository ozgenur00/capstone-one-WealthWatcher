import unittest
from datetime import datetime, timedelta
from app import app, db  # Adjust this import to where your Flask app and db are initialized
from models import User, Category, Budgets  # Ensure correct import paths

class TestBudgetModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up a test database and app context."""
        with app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        """Tear down the test database."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def setUp(self):
        """Create sample data before each test."""
        with app.app_context():
            self.user = User(first_name='John', last_name='Doe', username='johndoe', email='john@example.com', password='secure')
            self.category = Category(name='Utilities')
            db.session.add(self.user)
            db.session.add(self.category)
            db.session.commit()

    def tearDown(self):
        """Clean up the database after each test."""
        with app.app_context():
            db.session.query(User).delete()
            db.session.query(Category).delete()
            db.session.query(Budgets).delete()
            db.session.commit()

    def test_create_budget(self):
        """Test creation of a budget."""
        with app.app_context():
        # Preload necessary data within the context
            category = Category.query.get(self.category.id)
            user = User.query.get(self.user.id)
        
            budget = Budgets(
                category_name='Electricity',
                amount=150.00,
                spent=75.00,
                start_date=datetime.today().date(),
                end_date=datetime.today().date() + timedelta(days=30),
                created_at=datetime.now(),
                category_id=category.id,
                user_id=user.id
            )
            db.session.add(budget)
            db.session.commit()

            # Retrieve the budget to verify its properties
            retrieved = Budgets.query.first()
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved.category_name, 'Electricity')
            self.assertEqual(retrieved.amount, 150.00)
            self.assertEqual(retrieved.spent, 75.00)
            self.assertEqual(retrieved.user_id, user.id)
            self.assertEqual(retrieved.category_id, category.id)

if __name__ == '__main__':
    unittest.main()
