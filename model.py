from google.appengine.ext import ndb

class Status(object):
    saved = 1
    published = 2

class Post(ndb.Model):
    title        = ndb.StringProperty()
    content      = ndb.TextProperty()
    cover        = ndb.StringProperty()    
    published    = ndb.DateProperty()
    status       = ndb.IntegerProperty()
    date         = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def from_key(cls, key):
        post_key = ndb.Key(urlsafe=key)
        return post_key.get()

class Photo(ndb.Model):
    img_key = ndb.StringProperty()
    ref_key = ndb.StringProperty()
    caption = ndb.StringProperty()
    date    = ndb.DateTimeProperty(auto_now_add=True)



