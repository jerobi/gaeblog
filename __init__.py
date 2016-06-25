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
    # and a user object that has a properly authorized user 
    def __init__(self, jinja=None, base=None, user=None):
        self.base = base
        self.jinja = jinja
        self.user = user
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
    # class AdminPostsHandler(MainHandler):
    #
    #     def get(self):
    #         gaeb = gaeblog.GAEB(JINJA_ENVIRONMENT, 'templates/base.html', self._user)
    #         gaeb.posts_get(self)
    #
    #     def post(self):
    #         gaeb = gaeblog.GAEB(JINJA_ENVIRONMENT, 'templates/base.html', self._user)
    #         gaeb.posts_submit(self)
    #
    # class AdminHandler(MainHandler):
    #     def get(self):
    #         gaeb = gaeblog.GAEB(JINJA_ENVIRONMENT, 'templates/base.html', self._user)
    #         gaeb.admin(self)
    #
    # class AdminPhotoUploaderHandler(MainHandler):
    #     def get(self):
    #         gaeb = gaeblog.GAEB(JINJA_ENVIRONMENT, 'templates/base.html', self._user)
    #         gaeb.uploader(self)
    #
    # class AdminPhotoUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    #
    #    def post(self):
    #        gaeb = gaeblog.GAEB(JINJA_ENVIRONMENT, 'templates/base.html', self._user)
    #        gaeb.uploaded(self)
    #
    #
    # app = webapp2.WSGIApplication([
    #        ('/', MainHandler),
    #        ('/([^/]+)', PostHandler),
    #        ('/admin', AdminHandler),
    #        ('/admin/posts', AdminPostsHandler),
    #        ('/photo/upload', AdminPhotoUploadHandler),
    #        ('/photo/uploader', AdminPhotoUploaderHandler),
    # ], debug=True)

    def admin(self, handler):
        template = self.jinja.get_template('gaeblog/templates/admin.html')
        handler.response.write(template.render({
                    'base': self.base,
                    'user': self.user
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
    

    def _post_clean(self, post, category=None, tags=None, author=None):
        post_key = post.key.urlsafe()

        if category:
            category_name = category.name
        elif post.category_key:
            category = model.Category.from_key(post.category_key)
            category_name = category.name
        else:
            category_name = ''

        if not author:
            author = model.Author.from_key(post.author_key)
            
        if not tags:
            tags = model.Map.map(post_key, model.Map.Kind.postTag, model.Tag)

        return {
            'title'     : post.title,
            'key'       : post_key,
            'category'  : category_name,
            'cover'     : post.cover,
            'author'    : {
                'name' : author.name,
                'key'  : author.key.urlsafe()
                },
            'tags'      : [ t.name for t in tags ],
            'content'   : post.content,
            'status'    : post.status,
            'pubts'     : (post.published - datetime.datetime(1970,1,1)).total_seconds(),
            'published' : post.published.strftime('%Y-%m-%d')
            }

    def post(self, key):
        post = model.Post.from_key(key)
        return self._post_clean(post)

    def next(self, pubts):
        ref = datetime.datetime.fromtimestamp(pubts)
        posts = model.Post.query(ndb.AND(
                model.Post.status==model.Status.published,
                model.Post.published>ref
                )).order(model.Post.published).fetch(1)

        if posts:
            return self._post_clean(posts[0])
        else:
            return None

    def prev(self, pubts):
        ref = datetime.datetime.fromtimestamp(pubts)
        posts = model.Post.query(ndb.AND(
                model.Post.status==model.Status.published,
                model.Post.published<ref
                )).order(-model.Post.published).fetch(1)

        if posts:
            return self._post_clean(posts[0])
        else:
            return None
        

    def published(self, tag=None, category=None, author=None):
        # TODO : handle post query more efficiently 
        if tag:
            posts = model.Map.map(tag, model.Map.Kind.tagPost, model.Post)
        elif category:
            posts = model.Post.query(model.Post.status==model.Status.published, model.Post.category_key==category).order(-model.Post.published).fetch(100)
        elif author:
            posts = model.Post.query(model.Post.status==model.Status.published, model.Post.author_key==author).order(-model.Post.published).fetch(100)
        else:
            posts = model.Post.query(model.Post.status==model.Status.published).order(-model.Post.published).fetch(100)
        
        return [ self._post_clean(p) for p in posts if p.removed==0 and p.status==model.Status.published]

    def tags(self):
        tags = model.Tag.query().fetch(100)
        return [ (t.name, t.key.urlsafe()) for t in tags ]

    def categories(self):
        categories = model.Category.query().fetch(100)
        return [ (c.name, c.key.urlsafe()) for c in categories ]

    def posts_get(self, handler):
        posts = model.Post.query().order(-model.Post.published).fetch(100)

        handler.response.headers['Content-type'] = 'text/json'
        handler.response.write(json.dumps({
                    'status':0,
                    'data': [ self._post_clean(p) for p in posts ]
                    }))


    def _ensure_category(self, category):
        cat = model.Category.from_name_insert(category)
        return cat

    def _ensure_tags(self, tag_list, post_key):
        tags = []
        # first ensure that each tag exists
        for tag in tag_list:
            t = model.Tag.from_name_insert(tag)
            tags.append(t)
        tag_keys = [ t.key.urlsafe() for t in tags ]
        # clear out old mappings
        model.Map.clear(post_key, model.Map.Kind.postTag, model.Map.Kind.tagPost)
        # then make sure the tags are mapped to the post
        for tag_key in tag_keys:
            model.Map.ensure(tag_key, post_key, model.Map.Kind.tagPost)
            model.Map.ensure(post_key, tag_key, model.Map.Kind.postTag)
        # and return the tags
        return tags

    def _ensure_author(self):
        author = model.Author.from_user_insert(self.user)
        return author

    def posts_submit(self, handler):
        
        post_key = handler.request.get('key')
        published = handler.request.get('published')
        status = handler.request.get('status',1)

        if post_key:
            post = model.Post().from_key(post_key)
        else:
            post = model.Post()
            
        # create a datetime out of the date
        # where the time portion is stolen from today
        # this allows for better ordering on published
        pub_time = datetime.datetime.strptime(published, "%Y-%m-%d")
        now = datetime.datetime.now()
        mid = datetime.datetime.combine(now.date(), datetime.time(0))
        pub_time = pub_time + (now - mid)
        post.published = pub_time

        # ensure category and save to post
        cat_str = handler.request.get('category')
        if cat_str:
            category = self._ensure_category(cat_str)
            post.category_key = category.key.urlsafe()
        else:
            category = None

        # ensure author and save to post
        author = self._ensure_author()
        post.author_key = author.key.urlsafe()

        post.title = handler.request.get('title')
        post.content = handler.request.get('content')
        post.status = int(status)
        post.removed = 0
        post.cover = handler.request.get('cover')
        # pics = handler.request.get('pics')
        post.put()

        # ensure tags and create mappings
        tag_str = handler.request.get('tags')
        tag_list = [ t.strip() for t in tag_str.split(',') if t.strip() ]
        tags = self._ensure_tags(tag_list, post.key.urlsafe())
        

        handler.response.headers['Content-type'] = 'text/json'
        handler.response.write(json.dumps({
                    'status':0,
                    'data': self._post_clean(post, category=category, tags=tags, author=author) 
                    }))


