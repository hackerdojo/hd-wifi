""" Tests for main.py. """


# We need our external modules.
import appengine_config

import unittest
import urllib

import webtest

from google.appengine.api import memcache
from google.appengine.ext import testbed

from shared.auth import AuthHandler
import main


""" A base test class that sets everything up correctly. """
class BaseTest(unittest.TestCase):
  def setUp(self):
    # Set up testing for application.
    self.test_app = webtest.TestApp(main.app)

    # Set up datastore for testing.
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_memcache_stub()

  def tearDown(self):
    self.testbed.deactivate()


""" Tests that SplashHandler works. """
class SplashHandlerTest(BaseTest):
  """ Tests that getting the captive portal page with no parameters redirects as
  expected. """
  def test_no_parameters(self):
    response = self.test_app.get("/")

    self.assertEqual(302, response.status_int)
    self.assertEqual("http://www.hackerdojo.com", response.location)

  """ Tests that the page redirects correctly when we give it the parameters that
  the Meraki system would. """
  def test_meraki_redirect(self):
    params = {"base_grant_url": "foo", "user_continue_url": "bar"}
    query_str = urllib.urlencode(params)

    response = self.test_app.get("/?" + query_str)

    self.assertEqual(302, response.status_int)
    self.assertNotIn("base_grant_url", response.location)
    self.assertNotIn("user_continue_url", response.location)

    # Check that it wrote the cookie and saved stuff to memcache.
    token = self.test_app.cookies.get("grant_token")
    self.assertNotEqual(None, token)
    base_grant_url, user_continue_url = memcache.get(token)
    self.assertEqual("foo", base_grant_url)
    self.assertEqual("bar", user_continue_url)

  """ Tests that the page renders correctly. """
  def test_get(self):
    # Fake the cookie.
    self.test_app.set_cookie("grant_token", "notatoken")

    response = self.test_app.get("/")

    self.assertEqual(200, response.status_int)
    self.assertIn("/grant", response.body)


""" Tests that GrantHandler works. """
class GrantHandlerTest(BaseTest):
  def setUp(self):
    super(GrantHandlerTest, self).setUp()

    AuthHandler.simulate_user({"email": "testy.testerson@gmail.com"})

  """ Tests that it shows an error if the session does not exist. """
  def test_bad_session(self):
    response = self.test_app.get("/grant", expect_errors=True)

    self.assertEqual(401, response.status_int)
    self.assertIn("Session expired", response.body)

  """ Tests that it can grant us access successfully. """
  def test_grant(self):
    self.test_app.set_cookie("grant_token", "notatoken")
    memcache.set("notatoken", ["foo", "bar"])

    response = self.test_app.get("/grant")

    self.assertEqual(302, response.status_int)
    self.assertIn("foo?continue_url=bar", response.location)
