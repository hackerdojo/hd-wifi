import os

import jinja2

from shared.auth import AuthHandler


# Set up Jinja environment.
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


""" A base handler class for use on this project. """
class BaseHandler(AuthHandler):
  """ One-stop function for rendering a template.
  template: The path to the template.
  values: A dictionary of template values. The template values may also be
  supplied as keyword arguments.
  Returns: The rendered template HTML. """
  def render(self, template, values={}, **kwargs):
    values.update(kwargs)

    template = JINJA_ENVIRONMENT.get_template(template)
    return template.render(values)
