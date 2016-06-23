# import os
# import config
# import tornado.wsgi
# from urls import routs
# import tornado.ioloop
# import momoko
# from psycopg2.extras import DictCursor
# import tornado.httpserver
# from run import Application
#
# virtenv = os.environ['APPDIR'] + '/virtenv/'
# os.environ['PYTHON_EGG_CACHE'] = os.path.join(virtenv, 'lib/python3.3/site-packages')
# virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
# try:
#     with open(virtualenv) as f:
#         code = compile(f.read(), virtualenv, 'exec')
#         exec(code, dict(__file__=virtualenv))
# except IOError:
#     pass
#
# class Application(tornado.wsgi.WSGIApplication):
#     def __init__(self):
#         self.handlers = routs
#         ioloop = tornado.ioloop.IOLoop.instance()
#         self.settings = dict(
#             debug=config.DEBUG,
#             template_path=config.TEMPLATE_PATH,
#             static_path=config.STATIC_PATH,
#             cookie_secret='ss1sx!sdazxcccv2bfsdf232ggjhjjhjkjhk@!~s=d453',
#             login_url='/admin/login'
#         )
#         super(Application, self).__init__(self.handlers, **self.settings)
#         self.db_async = momoko.Pool(
#             dsn=config.get_db_url(),
#             size=1,
#             ioloop=ioloop,
#             cursor_factory=DictCursor
#         )
#         future = self.db_async.connect()
#         ioloop.add_future(future, lambda x: ioloop.stop())
#         ioloop.start()
#         future.result()
#
# def start_app():
#     app = Application()
#     http_server = tornado.httpserver.HTTPServer(app)
#     http_server.listen(8888)
#     tornado.ioloop.IOLoop.instance().start()
# application = start_app()
