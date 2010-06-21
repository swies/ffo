import tornado.web

class Post(tornado.web.UIModule):
    def render(self, p, comment_link=True):
        return self.render_string("module-post.html", p=p,
                                  comment_link=comment_link)
