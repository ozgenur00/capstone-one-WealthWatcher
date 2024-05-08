import unittest
from flask import Flask
from models import db, connect_db, Category

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///wealthwatcher_test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TESTING'] = True

with app.app_context():
    connect_db(app)
    db.create_all()

class CategoryModelTestCase(unittest.TestCase):
    def setUp(self):
        """Create test client and set up sample data."""
        with app.app_context():
            db.drop_all()
            db.create_all()
            self.client = app.test_client()

            # Adding a sample category
            self.category = Category(name="Utilities")
            db.session.add(self.category)
            db.session.commit()
            self.category_id = self.category.id

    def tearDown(self):
        """Clean up any fouled transaction."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_category_creation(self):
        """Test the creation of a category and verify its properties."""
        with app.app_context():
            category = db.session.get(Category, self.category_id)
            self.assertEqual(category.name, "Utilities")

    def test_category_query(self):
        """Test querying the category database to ensure data is retrieved correctly."""
        with app.app_context():
            category = db.session.query(Category).filter_by(name="Utilities").first()
            self.assertIsNotNone(category)
            self.assertEqual(category.name, "Utilities")

if __name__ == '__main__':
    unittest.main()
