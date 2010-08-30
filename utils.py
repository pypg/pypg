#!/usr/bin/env python
#
"""
utils module implements handler classes provided for convenience
"""
__author__ = 'Massimiliano Pippi <masci@evonove.it>'

from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp import template

import os

class BaseHandler(webapp.RequestHandler):
    """Base handler implementing a shortcut to render templates and serve
    error pages
    """
    def render_template(self, file, template_args=None):
        if template_args is None:
            template_args = {}
        path = os.path.join(os.path.dirname(__file__), "templates", file)
        self.response.out.write(template.render(path, template_args))
    
    def fail_not_found(self):
        self.error(404)
        self.render_template('404.html')
    
    def fail_auth(self):
        self.error(401)
        self.render_template('401.html')
    
    def fail_login_required(self):
        self.redirect(users.create_login_url("/"))

class NotFoundHandler(BaseHandler):
    """Generic catch-all handler for 404 pages"""
    def get(self):
        self.fail_not_found()
