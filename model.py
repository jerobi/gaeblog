from google.appengine.ext import ndb

class Post(ndb.Model):
    title        = ndb.StringProperty()
    content      = ndb.StringProperty()
    cover        = ndb.StringProperty()    
    published    = ndb.DateProperty()
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



