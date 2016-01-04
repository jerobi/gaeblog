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
import logging
import json
import base64
import datetime

from google.appengine.api import images
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

import model

class GAEB(object):

    # in order for GAEB to render templates in a style appropriate to the website
    # the caller should initialize with a jinja environment
    # and a base template that would contain css to style controls
    def __init__(self, jinja=None, base=None):
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

    def admin(self, handler):
        template = self.jinja.get_template('gaeblog/templates/admin.html')
        handler.response.write(template.render({
                    'base': self.base
                    }))

    def uploader(self, handler):
        # grab a url for uploading
        upload_url = blobstore.create_upload_url('/photo/upload')

        photo_key = handler.request.get('photo_key', None)
        
        if photo_key:
            photo_url = images.get_serving_url(photo_key)
        else:
            photo_url = None

        error = handler.request.get('error', '')

        # this will be a generic uploader that should be used within an iframe
        # the response to this will be piped to PhotoUploadHandler
        # which will redirect to the responder 
        template = self.jinja.get_template('gaeblog/templates/uploader.html')
        handler.response.write(template.render({
                    'upload_url' : upload_url,
                    'photo_key'  : photo_key,
                    'photo_url'  : photo_url,
                    'error'      : error
                    }))

    def uploaded(self, handler):
        try:
            upload = handler.get_uploads()[0]
            handler.redirect('/photo/uploader?photo_key=%s' % upload.key())
        except:
            handler.redirect('/photo/uploader?error=true')
    

    def _post_clean(self, post):
        return {
            'title'     : post.title,
            'key'       : post.key.urlsafe(),
            'content'   : post.content,
            'status'    : post.status,
            'published' : post.published.strftime('%Y-%m-%d')
            }

    def published(self, handler):
        posts = model.Post.query(model.Post.status==model.Status.published).order(-model.Post.published).fetch(100)
        return [ self._post_clean(p) for p in posts ]


    def posts_get(self, handler):
        posts = model.Post.query().order(-model.Post.published).fetch(100)

        handler.response.headers['Content-type'] = 'text/json'
        handler.response.write(json.dumps({
                    'status':0,
                    'data': [ self._post_clean(p) for p in posts ]
                    }))

    def posts_submit(self, handler):
        
        post_key = handler.request.get('key')
        published = handler.request.get('published')
        status = handler.request.get('status',1)

        if post_key:
            post = model.Post().from_key(post_key)
        else:
            post = model.Post()
            
        post.title = handler.request.get('title')
        post.published = datetime.datetime.strptime(published, "%Y-%m-%d").date()
        post.content = handler.request.get('content')
        post.status = int(status)
        # post.cover = handler.request.get('cover')
        # pics = handler.request.get('pics')
        post.put()

        handler.response.headers['Content-type'] = 'text/json'
        handler.response.write(json.dumps({
                    'status':0,
                    'data': self._post_clean(post) 
                    }))


