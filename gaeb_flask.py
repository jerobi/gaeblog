#!/usr/bin/env python
#
# Copyright 2016 Jeremiah Robison

import flask
from werkzeug.http import parse_cache_control_header, parse_options_header

from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

# Handler conformant to Flask 
class FlaskHandler(object):
    def render(self, path, params, content_type=None):
        if content_type is None:
            return flask.render_template(path, **params)
        else:
            content = flask.render_template(path, **params)
            response = flask.make_response(content)
            response.headers["Content-Type"] = content_type    
            return response

    def json(self, params):
        return flask.jsonify(params)

    def get_param(self, param, default):
        return flask.request.args.get(param, default)

    def post_param(self, param, default):
        return flask.request.form.get(param, default)

    def upload_url(self, url, secure):
        return blobstore.create_upload_url(url)

    def upload(self, secure):
        f = flask.request.files.get('img')
        
        if f:
            header = f.headers['Content-Type']
            parsed_header = parse_options_header(header)
            photo_key = parsed_header[1]['blob-key']
            photo_url = images.get_serving_url(photo_key, secure_url=secure)
            return (photo_key, photo_url)

        return (None, None)
