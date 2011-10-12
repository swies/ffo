#!/usr/bin/env python
'''
create table posts (
    id int auto_increment primary key,
    linkhash varchar(250),
    author varchar(250),
    title text,
    link text,
    summary text,
    tags text,
    posted_at datetime,
    checks integer default 0,
    comments integer default 0,
    key (linkhash)
) engine='innoDB', character set = 'utf8';
'''

import calendar
import feedparser
import hashlib
import simplejson as json
import time
import tornado.database

# feed_url = 'http://feeds.delicious.com/v2/rss/network/funfriends?plain&count=100'
# feed = feedparser.parse(feed_url)

def add_from_feed(feed):
    for p in feed.entries:
        if p.link.startswith('http://feeds.delicious.com/v2/rss/') and p.title == '404 Not Found':
            # skip missing users
            continue
        linkhash = hashlib.md5(p.link).hexdigest()
        # assume we're unique on linkhash and author
        if db.get('select id from posts where linkhash = %s and author = %s',
                  linkhash, p.author):
            continue
        tags = [t.term for t in p.get('tags', []) if t.term and not t.term.startswith(u'system:')]
        t = p.updated_parsed
        #t = time.localtime(calendar.timegm(t)) # convert to local time
        t = time.strftime('%Y-%m-%d %H:%M:%S', t) # convert to string
        db.execute('insert into posts (linkhash, author, title, ' + 
                           'link, summary, tags, posted_at) values ' +
                           '(%s, %s, %s, %s, %s, %s, %s)',
                           linkhash,
                           p.author,
                           p.title,
                           p.link,
                           p.get('summary', ''),
                           json.dumps(tags),
                           t)

db = tornado.database.Connection('localhost', 'ffo', 'root', '')

for user in db.query('select display_name from users'):
    feed_url = 'http://feeds.delicious.com/v2/rss/%s?plain&count=10' % user.display_name
    add_from_feed(feedparser.parse(feed_url))