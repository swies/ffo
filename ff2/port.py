#!/usr/bin/env python

import hashlib
import json
import tornado.database

ffo = tornado.database.Connection('localhost', 'ffo', 'root', '')
ff2 = tornado.database.Connection('localhost', 'ff2', 'root', '')

ff2_id = {} # ff2 id to ffo id mapping
ff2_name = {} # ff2 id to display_name mapping

def make_maps():
    hand_map = {
        'supersirhely': 'scadventures',
        'jack': 'jackkitzler',
        'riff market': 'rifftrafft',
        'frankie katzman': 'fkatz',
    }
    for u in ff2.iter('select id, name from users'):
        name = u.name.lower()
        name = hand_map.get(name, name)
        n = ffo.get('select id, display_name from users where lower_name = %s', name)
        if n:
            ff2_id[u.id] = n.id
            ff2_name[u.id] = n.display_name
        else:
            ff2_name[u.id] = u.name

def port_userinfo():
    '''
alter table users add column ff2_password varchar(32);
alter table users add column email varchar(250);
    '''
    for u in ff2.iter('select id, email, password from users'):
        if u.id not in ff2_id:
            continue
        ffo.execute('update users set ff2_password=%s, email=%s where id=%s',
                    u.password, u.email, ff2_id[u.id])
    ffo.execute('update users set ff2_password=NULL where password is not NULL')

def get_id(linkhash, author):
    r = ffo.get('select id from posts where linkhash=%s and author=%s',
                linkhash, author)
    if r:
        return r.id
    return None

def port_data():
    for p in ff2.query('select id, user, url, title, stamp, notes from posts'):
        tags = []
        for c in ff2.iter('select name from tags where postID = %s order by rank asc', p.id):
            tags.append(c.name)
        tags = json.dumps(tags)
        author = ff2_name[p.user]
        linkhash = hashlib.md5(p.url).hexdigest()
        if not get_id(linkhash, author):
            ffo.execute('insert into posts (linkhash, author, title, ' +
                        'link, summary, tags, posted_at) values (%s, ' +
                        '%s, %s, %s, %s, %s, %s)', linkhash, author,
                        p.title, p.url, p.notes, tags, p.stamp)
        i = get_id(linkhash, author)
        for c in ff2.iter('select user, text, stamp from comments where post = %s', p.id):
            ffo.execute('insert into comments (post_id, user_id, ' +
                        'comment, created_at) values (%s, %s, %s, %s)',
                        i, ff2_id[c.user], c.text, c.stamp)
        for c in ff2.iter('select user from recs where post = %s', p.id):
            # detect duplicate checks
            if not ffo.get('select post_id from checks where post_id=%s ' +
                           'and user_id=%s', i, ff2_id[c.user]):
                ffo.execute('insert into checks (post_id, user_id) ' +
                            'values (%s, %s)', i, ff2_id[c.user])

def main():
    ffo.execute('begin')
    make_maps()
    port_userinfo()
    port_data()
    ffo.execute('commit')
    ffo.execute('update posts set checks=' +
                '(select count(*) from checks where post_id=posts.id), ' +
                'comments=' +
                '(select count(*) from comments where post_id=posts.id)')

if __name__ == '__main__':
    main()
