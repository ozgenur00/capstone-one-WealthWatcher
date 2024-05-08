from flask import Flask
from models import db, connect_db, User, Accounts
import unittest
from sqlalchemy.orm import joinedload

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///wealthwatcher_test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TESTING'] = True

with app.app_context():
    connect_db(app)
    db.create_all()

class AccountsModelTestCase(unittest.TestCase):
    def setUp(self):
        """Create test client and add sample data."""
        with app.app_context():
            db.drop_all()
            db.create_all()
            self.client = app.test_client()

            
            self.user = User(first_name="John", last_name="Doe", username="johndoe", email="john@example.com", password="password")
            db.session.add(self.user)
            db.session.commit()

            
            db.session.refresh(self.user)

    def test_accounts_model(self):
        """Test creating an account and fetching it by ID."""
        with app.app_context():
            account = Accounts(name="Checking Account", account_type="Checking", balance=1500.00, user_id=self.user.id)
            db.session.add(account)
            db.session.commit()

            fetched_account = db.session.get(Accounts, account.id)
            
            self.assertEqual(fetched_account.name, "Checking Account")
            self.assertEqual(fetched_account.account_type, "Checking")
            self.assertEqual(fetched_account.balance, 1500.00)
            self.assertEqual(fetched_account.user_id, self.user.id)
            self.assertEqual(fetched_account.user.first_name, "John")

if __name__ == '__main__':
    unittest.main()
