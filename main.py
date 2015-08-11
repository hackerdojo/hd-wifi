from google.appengine.api import memcache

from webapp2_extras import security
import webapp2

from shared.auth import AuthHandler
from base_handler import BaseHandler


""" Deals with displaying the captive portal intro page. """
class SplashHandler(BaseHandler):
  def get(self):
    # Get the parameters that Meraki sends to us.
    base_grant_url = self.request.get("base_grant_url")
    user_continue_url = self.request.get("user_continue_url")

    if (not base_grant_url or not user_continue_url):
      if not self.request.cookies.get("grant_token"):
        # We should really only be getting here through the Meraki AP, so if
        # we're not, just send us back to the main website.
        self.redirect("http://www.hackerdojo.com")
        return

      # Otherwise, we're good to go.
      response = self.render("templates/splash.html", login_url="/grant")
      self.response.out.write(response)
      return

    # Save them to memcache.
    token = security.generate_random_string(12)
    memcache.set(token, [base_grant_url, user_continue_url])
    self.response.set_cookie("grant_token", token)

    # Hide the parameters.
    redirect_url = self._remove_params(["base_grant_url", "user_continue_url"])
    self.redirect(redirect_url)


""" Grants access to the user once they have logged in. """
class GrantHandler(BaseHandler):
  @AuthHandler.login_required
  def get(self):
    # Get the info we need to grant access.
    token = self.request.cookies.get("grant_token")
    if not token:
      response = self.render("templates/error.html", message="Session expired.")
      self.response.out.write(response)
      self.response.set_status(401)
      return
    grant_info = memcache.get(token)
    if not grant_info:
      response = self.render("templates/error.html", message="Session expired.")
      self.response.out.write(response)
      self.response.set_status(401)
      return

    base_grant_url, user_continue_url = grant_info

    # Clean up after ourselves.
    self.response.delete_cookie("grant_token")
    memcache.delete(token)

    # Tell the Meraki system to grant access.
    url = "%s?continue_url=%s" % (base_grant_url, user_continue_url)
    self.redirect(url)


app = webapp2.WSGIApplication([
    ("/", SplashHandler),
    ("/grant", GrantHandler)], debug=True)
