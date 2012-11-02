import os

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from splinter import Browser
from tests.base import BaseBrowserTests
from fake_webapp import EXAMPLE_APP

class PhantomJSTest(BaseBrowserTests, unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.browser = Browser('phantomjs')

    def setUp(self):
        self.browser.visit(EXAMPLE_APP)

    @classmethod
    def tearDownClass(self):
        self.browser.quit()


