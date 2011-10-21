# coding=utf-8


'''
create table comments (
    id int auto_increment primary key,
    post_id integer,
    user_id integer,
    comment text,
    created_at datetime,
    key (post_id),
    foreign key (post_id) references posts(id),
    foreign key (user_id) references users(id)
) engine='innoDB', character set = 'utf8';

create table checks (
    post_id integer,
    user_id integer,
    created_at datetime,
    primary key (post_id, user_id),
    foreign key (post_id) references posts(id),
    foreign key (user_id) references users(id)
) engine='innoDB', character set = 'utf8';
'''

import auth
import hashlib
import json
import re
import tornado.web
import util

class PostHandler(auth.SecuredHandler):
    def get(self, id):
        p = self.db.get('select id, linkhash, author, title, ' +
                        'link, summary, tags, posted_at, ' +
                        'checks, comments ' +
                        'from posts where id=%s',
                        id)
        if not p:
            raise tornado.web.HTTPError(404)
        self.postfix(p)
        comments = self.db.query('select user_id, comment, created_at ' +
                                 'from comments where post_id=%s ' +
                                 'order by created_at asc', id)
        # http://stackoverflow.com/questions/2026041/help-hacking-grubers-liberal-url-regex
        r = r'''\b((?:[a-z][\w-]+:(?:\/{1,3}|[a-z0-9%]))(?:[^\s()<>]+|\([^\s()<>]+\))+(?:\([^\s()<>]+\)|[^`!()\[\]{};:'".,<>?«»“”‘’\s]))'''
        r = re.compile(r, re.I)
        for c in comments:
            c['user'] = self.db.get('select display_name from users ' +
                                    'where id=%s', c.user_id).display_name
            c['ago'] = util.ago(c.created_at)
            # don't mess with HTML comments
            if '<' not in c.comment or '>' not in c.comment:
                c.comment = re.sub(r, r'<a href="\1">\1</a>', c.comment)
            c.comment = c.comment.replace('\n', '<br>')
        self.render('post.html', p = p, comments = comments)

    def post(self, id):
        '''add a comment'''
        p = self.db.get('select id from posts where id=%s', id)
        if not p:
            raise tornado.web.HTTPError(404)
        comment = self.get_argument('comment', '')
        if comment:
            self.db.execute('insert into comments (post_id, user_id, ' +
                            'comment, created_at) values (%s, %s, %s, ' +
                            'NOW())', id, self.current_user_id, comment)
            self.db.execute('update posts set comments=comments+1, ' +
                            'last_comment=NOW() where id=%s', id)
        self.redirect(self.request.path)


class NewPost(auth.SecuredHandler):
    def get(self):
        self.render('newpost.html', errors=[], title='', url='', tags='', description='')

    def post(self):
        errors = []
        url = self.get_argument('url', '')
        if not url:
            errors.append("You've got to enter a url")
        title = self.get_argument('title', '')
        if not title:
            errors.append("Every post needs a title")
        tags = self.get_argument('tags', '')
        description = self.get_argument('description', '')

        if errors:
            return self.render('newpost.html', errors=errors, title=title, url=url, tags=tags, description=description)

        linkhash = hashlib.md5(url).hexdigest()
        split_tags = []
        if tags.strip():
            split_tags = tags.split(' ')
        self.db.execute('insert into posts (linkhash, author, title, ' +
                           'link, summary, tags, posted_at) values ' +
                           '(%s, %s, %s, %s, %s, %s, NOW())',
                           linkhash,
                           self.current_user.lower(),
                           title,
                           url,
                           description,
                           json.dumps(split_tags))
        self.redirect('/')

class CheckHandler(auth.SecuredHandler):
    def post(self, id):
        '''add a check'''
        p = self.db.get('select id from posts where id=%s', id)
        if not p:
            raise tornado.web.HTTPError(404)
        if not self.user_did_check(id):
            self.db.execute('insert into checks (post_id, user_id, ' +
                            'created_at) values (%s, %s, NOW())',
                            id, self.current_user_id)
            self.db.execute('update posts set checks=checks+1 ' +
                            'where id=%s', id)
        self.write('OK')
