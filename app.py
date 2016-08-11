import tornado.web
import tornado.httpserver
import tornado.wsgi
from urls import routs
import config
import tornado.ioloop
import os
from psycopg2.extras import DictCursor
import momoko


class Application(tornado.web.Application):
    def __init__(self):
        self.handlers = routs
        ioloop = tornado.ioloop.IOLoop.instance()
        self.settings = dict(
            debug=config.DEBUG,
            template_path=config.TEMPLATE_PATH,
            static_path=config.STATIC_PATH,
            cookie_secret='ss1sx!sdazxcccv2bfsdf232ggjhjjhjkjhk@!~s=d453',
            login_url='/admin/login'
        )
        super(Application, self).__init__(self.handlers, **self.settings)
        self.db_async = momoko.Pool(
            dsn=config.get_db_url(),
            size=1,
            ioloop=ioloop,
            cursor_factory=DictCursor
        )
        future = self.db_async.connect()
        ioloop.add_future(future, lambda x: ioloop.stop())
        ioloop.start()
        future.result()


def start_app():
    app = Application()
    http_server = tornado.httpserver.HTTPServer(app, xheaders=True)
    http_server.listen(8080, os.environ.get('OPENSHIFT_PYTHON_IP', 'localhost'))
    print('Starting %s:%s' % (os.environ.get('OPENSHIFT_PYTHON_IP', 'localhost'), 8080))
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    start_app()
