"""
Test cases for Product Model

"""
import logging
import unittest
import os
from service.models import Product, DataValidationError, db
from service import app 

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)

######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
class TestProductModel(unittest.TestCase):
    """ Test Cases for Product Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

######################################################################
#  P L A C E   T E S T   C A S E S   H E R E 
######################################################################

    def test_XXXX(self):
        """ Test something """
        self.assertTrue(True)
