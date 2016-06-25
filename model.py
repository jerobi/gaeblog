from google.appengine.ext import ndb
import time

class Status(object):
    saved = 1
    published = 2

class Post(ndb.Model):
    title        = ndb.StringProperty()
    category_key = ndb.StringProperty()
    author_key   = ndb.StringProperty()
    content      = ndb.TextProperty()
    cover        = ndb.StringProperty()    
    published    = ndb.DateTimeProperty()
    status       = ndb.IntegerProperty()
    removed      = ndb.IntegerProperty()
    date         = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def from_key(cls, key):
        post_key = ndb.Key(urlsafe=key)
        return post_key.get()

    @classmethod
    def from_category(cls, category_key):
        posts = Post.query(Post.category_key==catgeory_key).fetch(100)
        return posts

class Photo(ndb.Model):
    img_key = ndb.StringProperty()
    ref_key = ndb.StringProperty()
    caption = ndb.StringProperty()
    removed = ndb.IntegerProperty()
    date    = ndb.DateTimeProperty(auto_now_add=True)

class Category(ndb.Model):
    name    = ndb.StringProperty()
    removed = ndb.IntegerProperty()
    date    = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def from_key(cls, key):
        post_key = ndb.Key(urlsafe=key)
        return post_key.get()

    @classmethod
    def from_name_insert(cls, name):
        cat = Category.query(Category.name==name).get()
        if not cat:
            cat = Category()
            cat.name = name
            cat.removed = 0
            cat.put();
        return cat


class Tag(ndb.Model):
    name    = ndb.StringProperty()
    removed = ndb.IntegerProperty()
    date    = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def from_key(cls, key):
        post_key = ndb.Key(urlsafe=key)
        return post_key.get()

    @classmethod
    def from_name_insert(cls, name):
        tag = Tag.query(Tag.name==name).get()
        if not tag:
            tag = Tag()
            tag.name = name
            tag.removed = 0
            tag.put();
        return tag

class Map(ndb.Model):
    left_key  = ndb.StringProperty()
    right_key = ndb.StringProperty()
    kind      = ndb.IntegerProperty()
    removed   = ndb.IntegerProperty()
    date      = ndb.DateTimeProperty(auto_now_add=True)

    class Kind(object):
        tagPost = 1
        postTag = 2

    @classmethod
    def map(cls, left_key, kind, inst):
        maps = Map.query(Map.left_key==left_key, Map.kind==kind, Map.removed==0).fetch(100)
        # perform lookup by class from mapping
        return [ inst.from_key(m.right_key) for m in maps ]
        
    @classmethod
    def clear(cls, key, left_kind, right_kind):
        left_maps = Map.query(Map.left_key==key, Map.kind==left_kind).fetch(100)
        for m in left_maps:
            m.removed = int(time.time())
            m.put()
        right_maps = Map.query(Map.right_key==key, Map.kind==right_kind).fetch(100)
        for m in right_maps:
            m.removed = int(time.time())
            m.put()
        

    @classmethod
    def ensure(cls, left_key, right_key, kind):
        map = Map.query(Map.left_key==left_key, Map.right_key==right_key, Map.kind==kind).get()
        if map:
            map.removed = 0
        else:
            map = Map()
            map.left_key = left_key
            map.right_key = right_key
            map.kind = kind
            map.removed = 0
            
        map.put();
        return map


class Author(ndb.Model):
    name       = ndb.StringProperty()
    lookup_key = ndb.StringProperty()
    photo_url  = ndb.StringProperty()
    removed    = ndb.IntegerProperty()
    date       = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def from_key(cls, key):
        author_key = ndb.Key(urlsafe=key)
        return author_key.get()


    @classmethod
    def from_user_insert(cls, user):
        author = Author.query(Author.lookup_key==user['lookup_key']).get()
        if not author:
            author = Author()
            author.name = user['name']
            author.lookup_key = user['lookup_key']
            author.photo_url = user.get('photo_url')
            author.removed = 0
            author.put();
        return author



