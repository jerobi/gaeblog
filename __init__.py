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


# data storage - may want to abstract this out as well
from google.appengine.ext import ndb
import model


from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ' '.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


class GAEB(object):

    # GAEB supports two flavors
    # 1. StandardHandler - Standard app engine request handler
    #
    #    from gaeblog.gaeb_standard import StandardHandler
    #    import gaeblog
    #
    #    see gaeblog.gaeb_standard for configuration
    #
    # 2. FlaskHandler - Handler that conforms to a Flask implementation
    #
    #    from gaeblog.gaeb_flask import FlaskHandler
    #    import gaeblog
    # 
    #    see gaeblog.gaeb_flask for configuration
    #
    def __init__(self, handler, user=None, secure=False):
        self.handler = handler
        self.user = user
        self.secure = secure
        self.pub_format = '%Y-%m-%d'
        self.preview_length = 140
        
    def set_pub_format(self, format):
        self.pub_format = format

    def set_preview_length(self, preview_length):
        self.preview_length = preview_length

    def admin(self, base=None, prefix=None):
        assert(self.user)
        return self.handler.render('gaeblog/templates/admin.html', {
                'base': base,
                'user': self.user,
                'prefix': prefix
                })

    def feed(self, title, description, source, hub='http://pubsubhubbub.appspot.com'):
                
        return self.handler.render('gaeblog/templates/atom.xml', {
                'title': title,
                'description': description,
                'hub': hub,
                'source': source,
                'posts': self.published()
                }, content_type = 'application/atom+xml')
                                   
                                   

    def uploader(self, url):
        # grab a url for uploading
        
        upload_url = self.handler.upload_url(url, self.secure)
        (photo_key, photo_url) = self.handler.upload(self.secure)

        error = self.handler.post_param('error', '')

        return self.handler.render('gaeblog/templates/uploader.html', {
                'upload_url' : upload_url,
                'photo_key'  : photo_key,
                'photo_url'  : photo_url,
                'error'      : error
                })
    
    def _preview(self, content):
        stripped = strip_tags(content)

        if len(stripped) < self.preview_length:
            return stripped

        splitted = stripped.split()
        content_len = 0
        content_index = 0
        while content_len < self.preview_length - 3:
            content_len += len(splitted[content_index]) + 1
            content_index += 1;
            
        return ' '.join(splitted[0:content_index]) + "..."


    def _post_clean(self, post, category=None, tags=None, author=None):
        post_key = post.key.urlsafe()

        if not category and post.category_key:
            category = model.Category.from_key(post.category_key)

        if category:
            category_dict = {
                'name' : category.name,
                'key'  : category.key.urlsafe(),
                'shortcode' : category.shortcode
                }
        else:
            category_dict = None

        if not author:
            author = model.Author.from_key(post.author_key)
            
        if not tags:
            tags = model.Map.map(post_key, model.Map.Kind.postTag, model.Tag)

        return {
            'title'     : post.title,
            'shortcode' : post.shortcode,
            'key'       : post_key,
            'category'  : category_dict,
            'cover'     : post.cover,
            'author'    : {
                'name' : author.name,
                'key'  : author.key.urlsafe(),
                'shortcode' : author.shortcode,
                },
            'tags'      : [ {
                    'key' : t.key.urlsafe(), 
                    'name' : t.name,
                    'shortcode' : t.shortcode
                    } for t in tags ],
            'content'   : post.content,
            'preview'   : self._preview(post.content),
            'status'    : post.status,
            'pubts'     : (post.published - datetime.datetime(1970,1,1)).total_seconds(),
            'published' : post.published.strftime(self.pub_format),
            'ztime'     : post.published.strftime('%Y-%m-%dT%H:%M:%SZ')
            }

    def post(self, shortcode):
        post = model.Post.from_shortcode(shortcode)
        return self._post_clean(post)

    def admin_post(self, key):
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
            obj = model.Tag.from_shortcode(tag)
            posts = model.Map.map(obj.key.urlsafe(), model.Map.Kind.tagPost, model.Post)
        elif category:
            obj = model.Category.from_shortcode(category)
            posts = model.Post.query(model.Post.status==model.Status.published, model.Post.category_key==obj.key.urlsafe()).order(-model.Post.published).fetch(100)
        elif author:
            obj = model.Author.from_shortcode(author)
            posts = model.Post.query(model.Post.status==model.Status.published, model.Post.author_key==obj.key.urlsafe()).order(-model.Post.published).fetch(100)
        else:
            posts = model.Post.query(model.Post.status==model.Status.published).order(-model.Post.published).fetch(100)
        
        return [ self._post_clean(p) for p in posts if p.removed==0 and p.status==model.Status.published]

    def label(self, tag=None, category=None, author=None):

        if tag:
            obj = model.Tag.from_shortcode(tag)
            return {
                'name':'tag',
                'value':obj.name
                }
        elif category:
            obj = model.Category.from_shortcode(category)
            return {
                'name':'category', 
                'value':obj.name
                }
        elif author:
            obj = model.Author.from_shortcode(author)
            return {
                'name':'author', 
                'value':obj.name
                }
        else:
            return None

    def tags(self):
        tags = model.Tag.query().fetch(100)
        return [ {
                'name' : t.name, 
                'key'  : t.key.urlsafe(),
                'shortcode' : t.shortcode
                } for t in tags ]

    def categories(self):
        categories = model.Category.query().fetch(100)
        return [ {
                'name' : c.name,
                'key'  : c.key.urlsafe(),
                'shortcode' : c.shortcode
                } for c in categories ]

    def posts_get(self):
        posts = model.Post.query().order(-model.Post.published).fetch(100)

        return self.handler.json({
                'status':0,
                'data': [ self._post_clean(p) for p in posts ]
                })


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
        assert(self.user)
        author = model.Author.from_user_insert(self.user)
        return author

    def posts_submit(self):

        post_key = self.handler.post_param('key', None)
        published = self.handler.post_param('published', None)
        status = self.handler.post_param('status', 1)

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
        cat_str = self.handler.post_param('category', None)
        if cat_str:
            category = self._ensure_category(cat_str)
            post.category_key = category.key.urlsafe()
        else:
            category = None

        # ensure author and save to post
        author = self._ensure_author()
        post.author_key = author.key.urlsafe()

        post.title = self.handler.post_param('title', None)
        post.shortcode = self.handler.post_param('shortcode', None)
        post.content = self.handler.post_param('content', None)
        post.status = int(status)
        post.removed = 0
        post.cover = self.handler.post_param('cover', None)
        # pics = handler.request.get('pics')
        post.put()
        

        # ensure tags and create mappings
        tag_str = self.handler.post_param('tags', None)
        tag_list = [ t.strip() for t in tag_str.split(',') if t.strip() ]
        tags = self._ensure_tags(tag_list, post.key.urlsafe())
        
        return self.handler.json({
                    'status':0,
                    'data': self._post_clean(post, category=category, tags=tags, author=author) 
                    })

        

