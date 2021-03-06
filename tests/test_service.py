"""
Product API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from urllib.parse import quote_plus
from flask_api import status  # HTTP Status Codes
from service.models import db, Product
from service.routes import app, init_db
from .factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)

######################################################################
#  T E S T   C A S E S
######################################################################

class TestProductServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db()

    def setUp(self):
        """ Runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def _create_product(self):
        # TODO Replace with create products once all test cases are update to reflect non fixed values
        # return _create_products(1)
        return Product(
            sku=12345,
            name="ABCchocolate", 
            category="food", 
            short_description="dark chocolate",
            long_description="lindts dark chocolate Christmas limited version",
            price=28,
            rating=4, 
            available=True,
            enabled = True, 
            likes = 10
        )

    def _create_products(self, count):
        """ Factory method to create products in bulk """
        products = []
        for _ in range(count):
            test_product = ProductFactory()
            resp = self.app.post(
                "/products", json=test_product.serialize(), content_type="application/json"
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test product"
            )
            new_product = resp.get_json()
            test_product.id = new_product["id"]
            products.append(test_product)
        return products


######################################################################
#  P L A C E   T E S T   C A S E S   H E R E 
######################################################################
    
    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # data = resp.get_json()
        # self.assertEqual(data["name"], "Product REST API Service")

    def test_get_product_list(self):
        """ Get a list of Products """
        self._create_product()
        resp = self.app.get("/products")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)

    def test_get_product(self):
        """ Get a single Product """
        # get the id of a pet
        test_product = self._create_product()
        test_product.create()
        resp = self.app.get(
            "/products/{}".format(test_product.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], test_product.name)

    def test_get_product_not_found(self):
        """ Get a Product thats not found """
        resp = self.app.get("/products/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_product_list_by_name(self):
        """ Query Products by Name """
        products = self._create_products(10)
        test_name = products[0].name
        name_products = [product for product in products if product.name == test_name]
        resp = self.app.get(
            "/products", query_string="name={}".format(quote_plus(test_name))
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(name_products))
        # check the data just to be sure
        for product in data:
            self.assertEqual(product["name"], test_name)

    def test_query_product_list_by_category(self):
        """ Query Products by Category """
        products = self._create_products(10)
        test_category = products[0].category
        category_products = [product for product in products if product.category == test_category]
        resp = self.app.get(
            "/products", query_string="category={}".format(quote_plus(test_category))
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(category_products))
        # check the data just to be sure
        for product in data:
            self.assertEqual(product["category"], test_category)

    def test_query_products_list_by_available(self):
        """Query Products by Available"""
        products = self._create_products(10)
        test_available = products[0].available
        available_products = [product for product in products if product.available == test_available]
        resp = self.app.get(
            "/products", query_string="available={}".format(test_available)
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(available_products))
        # check the data
        for product in data:
            self.assertEqual(product["available"], test_available)

    def test_query_products_list_by_rating(self):
        """Query Products by Rating"""
        products = self._create_products(10)
        test_rating = products[0].rating
        rating_products = [product for product in products if product.rating == test_rating]
        resp = self.app.get(
            "/products", query_string="rating={}".format(test_rating)
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(rating_products))
        # check the data
        for product in data:
            self.assertEqual(product["rating"], test_rating)

    def test_create_product(self):
        """ Create a new Product """
        test_product = self._create_product()
        logging.debug(test_product)
        resp = self.app.post(
            "/products", json=test_product.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_product = resp.get_json()
        self.assertEqual(new_product["id"], 1)
        self.assertEqual(new_product["sku"], test_product.sku)
        self.assertEqual(new_product["name"], test_product.name)
        self.assertEqual(new_product["category"], test_product.category)
        self.assertEqual(new_product["short_description"], test_product.short_description)
        self.assertEqual(new_product["long_description"], test_product.long_description)
        self.assertEqual(new_product["price"], test_product.price)
        self.assertEqual(new_product["rating"], test_product.rating)
        self.assertEqual(new_product["available"], test_product.available)

        # ToDo: Uncomment once retrieve product is implemented
        # # Check that the location header was correct
        # resp = self.app.get(location, content_type="application/json")
        # self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # new_product = resp.get_json()
        # self.assertEqual(new_product["sku"], test_product.sku)
        # self.assertEqual(new_product["name"], test_product.name)
        # self.assertEqual(new_product["category"], test_product.category)
        # self.assertEqual(new_product["short_description"], test_product.short_description)
        # self.assertEqual(new_product["long_description"], test_product.long_description)
        # self.assertEqual(new_product["price"], test_product.price)
        # self.assertEqual(new_product["rating"], test_product.rating)
        # self.assertEqual(new_product["stock_status"], test_product.stock_status)

    def test_update_product(self):
        """ Update an existing Product """
        # create a product to update
        test_product = self._create_product()
        test_product.create()
        resp = self.app.post(
            "/products", json=test_product.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the product
        new_product = resp.get_json()
        logging.debug(new_product)
        new_product["category"] = "unknown"
        resp = self.app.put(
            "/products/{}".format(new_product["id"]),
            json=new_product,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_product = resp.get_json()
        self.assertEqual(updated_product["category"], "unknown")

    def test_update_no_product(self):
        """ Update a Product without an ID """
        resp = self.app.put(
            "/products/{}".format(123),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_product(self):
        """ Delete a Product """
        test_product = self._create_product()
        test_product.create()
        resp = self.app.delete(
            "/products/{}".format(test_product.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get(
            "/products/{}".format(test_product.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_content_type(self):
        """ Test an invalid content type """
        test_product = self._create_product()
        test_product.create()
        resp = self.app.post(
            "/products", json=test_product.serialize(), content_type="test/"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_bad_request(self):
        """ Test a bad request """
        resp = self.app.post(
            "/products", json={"test": "test"}, content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_disable_product(self):
            """ Disable an existing Product """
            # create a product to disable
            test_product = self._create_products(1)[0]
            test_product.create()
            resp = self.app.post(
                "/products", json=test_product.serialize(), content_type="application/json"
            )
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

            # disable the product
            new_product = resp.get_json()
            logging.debug(new_product)
            resp = self.app.put(
                "/products/{}/disable".format(new_product["id"]),
                json=new_product,
                content_type="application/json",
            )
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            updated_product = resp.get_json()
            self.assertEqual(updated_product["enabled"], False)

    def test_like_product(self):
        """ Like an existing Product """
        # create a product to like
        test_product = self._create_products(1)[0]
        test_product.create()
        resp = self.app.post(
            "/products", json=test_product.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # like the product
        new_product = resp.get_json()
        logging.debug(new_product)
        resp = self.app.put(
            "/products/{}/like".format(new_product["id"]),
            json=new_product,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_product = resp.get_json()
        self.assertEqual(updated_product["likes"], test_product.likes + 1)

    def test_like_no_product(self):
        """ Like an non-existing Product """
        
        # like the product
        resp = self.app.put(
                "/products/{}/like".format(456),
                content_type="application/json",
            )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_disable_no_product(self):
        """ Disable an non-existing Product """
        
        # disable the product
        resp = self.app.put(
                "/products/{}/disable".format(456),
                content_type="application/json",
            )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)