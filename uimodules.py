import tornado.web
import embedly

class Post(tornado.web.UIModule):
    def render(self, p, comment_link=True):
        return self.render_string("module-post.html", p=p,
                                  embedly=embedly.embedly_re.match(p.link),
                                  comment_link=comment_link)
