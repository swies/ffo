import base64
import datetime
import os

def path(*args):
    here = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(here, *args)

def random(bytes=5):
    return base64.b32encode(os.urandom(bytes))

def yesterday(days=1):
    return datetime.datetime.now() - datetime.timedelta(days=days)

def div(a, b):
    '''divide, but not by zero'''
    b = float(b)
    if b == 0.0:
        return 0.0
    return a/b

def debug():
    '''are we running on a dev machine?'''
    return os.uname()[1] in ('bauxite', 'bauxite.local', 'raven')

def ago(t):
    '''format a nice x seconds/minutes/days/months ago thing'''
    def ret(s, unit):
        '''properly pluralize return value'''
        if s == 1: return '%d %s ago' % (s, unit)
        return '%d %ss ago' % (s, unit)
    d = datetime.datetime.utcnow() - t
    s = d.seconds + (60*60*24*d.days)
    if s <= 0:
        return 'just now'
    if s < 60:
        return ret(s, 'second')
    s /= 60
    if s < 60:
        return ret(s, 'minute')
    s /= 60
    if s < 24:
        return ret(s, 'hour')
    s /= 24
    if s < 7:
        return ret(s, 'day')
    s /= 7
    return ret(s, 'week')
