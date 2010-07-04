#!/usr/bin/env python

import datetime
import sys
import simplejson as json
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
        try: page = int(page)
        except: page = 0
        if page < 0: page = 0
        limit = 25
        posts = self.db.query('select id, linkhash, author, title, ' +
                              'link, summary, tags, posted_at, ' +
                              'checks, comments ' +
                              'from posts order by posted_at desc ' +
                              'limit %s offset %s',
                              limit, page*limit)
        for p in posts:
            self.postfix(p)
        self.render('index.html', posts=posts, page=page)
        #newusers = self.db.query('select count(*) as c from auth_user where date_joined >= %s;', util.yesterday())[0].c
        #live = self.db.query('select count(*) as c from rain_subscription where auto_renew = 1;')[0].c
        #self.render('index.html', date = datetime.date,
        #                          newusers = newusers,
        #                          live = live)

application = tornado.web.Application([
    (r'/', MainHandler),

    (r'/claim', auth.Claim),
    (r'/signin', auth.SignIn),
    (r'/signout', auth.SignOut),

    (r'/post/([0-9]+)', post.PostHandler),
    (r'/post/([0-9]+)/check', post.CheckHandler),
],
    static_url_prefix = '/static/',
    static_path = util.path('static'),
    template_path = util.path('templates'),
    cookie_secret = '$2a$12$R.EjZxzYFVOSSj3W8pL6VulA9hGXevmhArqRP5drlG0upm5U4l4LK',
    debug = util.debug(),
    ui_modules = uimodules,
)

if __name__ == '__main__':
    port = 8000
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()
