import tornado.database

class DBMixin():
    @property
    def db(self):
        if not hasattr(self, '_db'):
            self._db = tornado.database.Connection('localhost',
                                                   'ffo',
                                                   'root', '')
        return self._db
