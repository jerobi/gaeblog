#!/usr/bin/env python
#
# Copyright 2015 jerobi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import webapp2
import jinja2
import logging
import json
import base64

class GAEB(object):

    # in order for GAEB to render templates in a style appropriate to the website
    # the caller should initialize with a jinja environment
    # and a base template that would contain css to style controls
    def __init__(self, jinja, base):
        self.base = base
        self.jinja = jinja
        pass
    
    # example of an admin class in GAE main.py to call admin
    # import os
    # import webapp2
    # import jinja2
    # import gaeblog

    # JINJA_ENVIRONMENT = jinja2.Environment(
    #     loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    #     extensions=['jinja2.ext.autoescape'],
    #     autoescape=True)
 
    #
    # class AdminHandler(MainHandler):
    #     @basicauth('admin:admin')
    #     def get(self):
    #         gaeb = gaeblog.GAEB(JINJA_ENVIRONMENT, 'templates/base.html')
    #         self.response.write(gaeb.admin())
    #
    # app = webapp2.WSGIApplication([
    #     ('/', MainHandler),
    #     ('/admin', AdminHandler)
    # ], debug=True)

    def admin(self):
        template = self.jinja.get_template('gaeblog/templates/admin.html')
        return template.render({
                'base': self.base
                })
    

