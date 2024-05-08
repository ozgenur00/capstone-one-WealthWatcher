# # test_transactions.py
# from flask import Flask
# from datetime import datetime
# from models import db, connect_db, User, Accounts, Category, Transactions
# import unittest

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///wealthwatcher_test'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['TESTING'] = True

# with app.app_context():
#     connect_db(app)
#     db.create_all()

# class TransactionsModelTestCase(unittest.TestCase):
#     def setUp(self):
#         with app.app_context():
#             db.drop_all()
#             db.create_all()
#             self.client = app.test_client()

#             # Setup User
#             self.user = User(first_name="Bob", last_name="Builder", username="bobbuilder", email="bob@example.com", password="buildit")
#             db.session.add(self.user)
#             db.session.commit()  # Commit to ensure user_id is available

#             # Setup Account
#             self.account = Accounts(name="Savings", account_type="Savings", balance=20000.00, user_id=self.user.id)
#             db.session.add(self.account)
#             db.session.commit()  # Commit the account

#             # Re-attach account to the session to avoid DetachedInstanceError
#             db.session.add(self.account)
#             db.session.refresh(self.account)

#             # Setup Category
#             self.category = Category(name="Tools")
#             db.session.add(self.category)
#             db.session.commit()  # Commit to ensure category_id is available

#             # Create Transaction
#             self.transaction = Transactions(
#                 type="Expense",
#                 description="Hammer",
#                 amount=29.99,
#                 date=datetime.now().date(),
#                 category_id=self.category.id,
#                 account_id=self.account.id,
#                 user_id=self.user.id
#             )
#             db.session.add(self.transaction)
#             db.session.commit()

#     def test_transactions_model(self):
#         with app.app_context():
#             # Access transaction within the same session context
#             fetched_transaction = db.session.get(Transactions, self.transaction.id)
#             self.assertIsNotNone(fetched_transaction)
#             self.assertEqual(fetched_transaction.description, "Hammer")

#             # Access account to verify no DetachedInstanceError
#             self.assertIsNotNone(self.account.user)
#             self.assertEqual(self.account.user_id, self.user.id)

# if __name__ == '__main__':
#     unittest.main()
