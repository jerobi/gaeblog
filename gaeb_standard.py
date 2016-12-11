#!/usr/bin/env python
#
# Copyright 2016 Jeremiah Robison

import json
import logging

from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

# Handler conformant to Standard GAE Request Handlers 
class StandardHandler(object):
    def __init__(self, handler, jinja=None):
        self.handler = handler
        self.jinja = jinja

    def render(self, path, params, content_type=None):
        
        template = self.jinja.get_template(path)
        if content_type:
            self.handler.response.headers['Content-type'] = content_type
        return self.handler.response.write(template.render(params))
        

    def json(self, params):
        self.handler.response.headers['Content-type'] = 'text/json'
        return self.handler.response.write(json.dumps(params))

    def get_param(self, param, default):
        return self.handler.request.get(param, default)

    def post_param(self, param, default):
        return self.handler.request.get(param, default)

    def upload_url(self, url, secure):
        return blobstore.create_upload_url(url)

    def upload(self, secure):
        uploads = self.handler.get_uploads()
       
        if len(uploads) >= 1:
            photo_key = uploads[0].key()
            photo_url = images.get_serving_url(photo_key, secure_url=secure)
            return (photo_key, photo_url)

        return (None, None)


        

