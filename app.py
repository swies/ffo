#!/usr/bin/env python

import datetime
import sys
import json
import tornado.httpserver
import tornado.ioloop
import tornado.web

import auth
import util
import post
import uimodules

class MainHandler(auth.BaseHandler):
    def get(self):
        page = self.get_argument('page', '0')
        try:
            page = int(page)
        except:
            page = 0
        if page < 0:
            page = 0

        limit = 25

        sort = self.get_argument('sort', 'post')
        order_by = 'posted_at'
        if sort == 'comment':
            order_by = 'last_comment'

        posts = self.db.query('select id, linkhash, author, title, ' +
                              'link, summary, tags, posted_at, ' +
                              'checks, comments ' +
                              'from posts order by ' + order_by +
                              ' desc ' +
                              'limit %s offset %s',
                              limit, page*limit)
        for p in posts:
            self.postfix(p)
        self.render('index.html', posts=posts, page=page, sort=sort)

application = tornado.web.Application([
    (r'/', MainHandler),

    (r'/signin', auth.SignIn),
    (r'/signout', auth.SignOut),
    (r'/passwd', auth.Passwd),

    (r'/post/([0-9]+)', post.PostHandler),
    (r'/post/([0-9]+)/check', post.CheckHandler),
],
    static_url_prefix = '/static/',
    static_path = util.path('static'),
    template_path = util.path('templates'),
    cookie_secret = util.secret(),
    debug = util.debug(),
    ui_modules = uimodules,
    autoescape = None,
)

if __name__ == '__main__':
    port = 8000
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()
