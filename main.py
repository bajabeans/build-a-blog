#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Blog(db.Model):
    title = db.StringProperty(required = True)
    blog = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class MainPage(Handler):
    def render_front(self, title="", blog="", error="", content="", titlepost=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")

        self.render("form.html", title=title, blog=blog, error=error, blogs=blogs, content=content, titlepost=titlepost)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        blog = self.request.get("blog")

        if title and blog:
            a = Blog(title = title, blog = blog)
            a.put()

            self.redirect("/blog/%s" % a.key().id())

        else:
            error = "need both a title and a blog post!"
            self.render("form.html", error = error, content = blog, titlepost = title)

class Recent(Handler):
    def render_blog(self, title="", blog=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC")

        self.render("recentpost.html", title=title, blog=blog, blogs=blogs)

    def get(self):

        self.render_blog()

class NewPost(Handler):
    def render_new(self, title="", blog="", error= "", content="", titlepost=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC")

        self.render("newpost.html", title=title, blog=blog, error=error, blogs=blogs, content=content, titlepost=titlepost)

    def get(self):
        self.render_new()

    def post(self):
        title = self.request.get("title")
        blog = self.request.get("blog")


        if title and blog:
            blogpost = Blog(title = title, blog = blog)
            blogpost.put()

            self.redirect("/blog/%s" % blogpost.key().id())

        else:
            error = "need both a title and a blog post!"

            self.render("newpost.html", error = error, content = blog, titlepost = title)

class ViewPostHandler(Handler):
    def render_singlepost(self, title="", blog=""):
        self.render("singlepost.html", title=title, blog=blog)



    def get(self,id):
        #title = self.request.get("title")
        #blog = self.request.get("blog")
  # returning a string -- need to figure out how to get id
  #value="{{ movie.key().id() }}" ???
        #bid = blog_id.key().id()
        blog = Blog.get_by_id(int(id))
        title = blog.title
        blog = blog.blog

        #self.response.write(blog)
        self.render_singlepost(title = title, blog = blog)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', Recent),
    ('/new', NewPost),
    webapp2.Route('/blog/<id:\d+>',ViewPostHandler)
], debug=True)
