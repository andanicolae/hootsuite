import unittest
import web_server.web_server as web_server
from utils.http_exception import InvalidUsage

class WebServerTest(unittest.TestCase):

    def test_mandatory_subreddit(self):
        self.assertRaises(InvalidUsage, web_server.validate_input, None, 1, 2)

    def test_mandatory_from(self):
        self.assertRaises(InvalidUsage, web_server.validate_input, "Python", None, 1)

    def test_mandatory_to(self):
        self.assertRaises(InvalidUsage, web_server.validate_input, "Scala", 1.34320535, None)
