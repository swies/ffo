#!/usr/bin/env python
'''
create table users (
    id int auto_increment primary key,
    lower_name varchar(250) unique,
    password varchar(250),
    display_name varchar(250),
    claimed_at datetime,
    claimed_by_ip varchar(15)
) engine='innoDB', character set = 'utf8';
'''

import feedparser
import tornado.database

feed_url = 'http://feeds.delicious.com/v2/rss/networkmembers/funfriends'
feed = feedparser.parse(feed_url)

db = tornado.database.Connection('localhost', 'ffo', 'root', '')

for name in (e.title for e in feed.entries):
    db.execute('insert into users (lower_name, display_name) values (%s, %s)', name.lower(), name)
