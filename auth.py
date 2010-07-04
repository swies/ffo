import bcrypt
import db
import hashlib
import simplejson as json
import tornado.web
import util

cookie_name = 'user'

class BaseHandler(tornado.web.RequestHandler, db.DBMixin):
    def get_current_user(self):
        return self.get_secure_cookie(cookie_name)

    @property
    def current_user_id(self):
        if not self.current_user:
            return None
        if not hasattr(self, '_current_user_id'):
            u = self.db.get('select id from users where display_name=%s',
                            self.current_user)
            if not u:
                return None
            self._current_user_id = u.id
        return self._current_user_id

    def user_did_check(self, post_id):
        '''did the user check a post?'''
        if not self.current_user:
            return False
        c = self.db.get('select user_id from checks where ' +
                        'post_id=%s and user_id=%s',
                        post_id, self.current_user_id)
        return not not c

    def postfix(self, p):
        p['taglist'] = json.loads(p.tags)
        p['ago'] = util.ago(p.posted_at)
        p['didcheck'] = self.user_did_check(p.id) 

class SecuredHandler(BaseHandler):
    def prepare(self):
        if not self.current_user:
            self.redirect('/signin?next='+self.request.path)
    
class SignIn(BaseHandler):
    def get(self, user='', flash=''):
        self.render('signin.html', user=user, flash=flash)

    def post(self):
        user = self.get_argument('name', '')
        pw = self.get_argument('pw', '')
        next = self.get_argument('next', '/')
        if not next.startswith('/'):
            next = '/'
        u = self.db.get('select id, display_name, password, ff2_password ' +
                        'from users where lower_name=%s', user.lower())
        if u:
            if u.ff2_password:
                if hashlib.md5(pw).hexdigest() == u.ff2_password:
                    self.db.execute('update users set password=%s, ' +
                                    'ff2_password=NULL, ' +
                                    'claimed_at=NOW(), ' +
                                    'claimed_by_ip=%s where id=%s',
                                    bcrypt.hashpw(pw, bcrypt.gensalt()),
                                    self.request.remote_ip,
                                    u.id)
                    self.set_secure_cookie(cookie_name, u.display_name)
                    return self.redirect(next)
            elif u.password:
                if bcrypt.hashpw(pw, u.password) == u.password:
                    self.db.execute('update users set ' +
                                    'claimed_by_ip=%s where id=%s',
                                    self.request.remote_ip, u.id)
                    self.set_secure_cookie(cookie_name, u.display_name)
                    return self.redirect(next)
        return self.get(user=user, flash='Sign In Failed.')

class SignOut(BaseHandler):
    def get(self):
        self.clear_cookie(cookie_name)
        self.render('signout.html', current_user=None)
