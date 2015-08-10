import webapp2

from base_handler import BaseHandler


""" Deals with displaying the captive portal intro page. """
class SplashHandler(BaseHandler):
  def get(self):
    response = self.render("templates/splash.html")
    self.response.out.write(response)


app = webapp2.WSGIApplication([
    ("/", SplashHandler)], debug=True)
