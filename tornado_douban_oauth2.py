# -*- coding: utf-8 -*-
import os
import tornado.web
import tornado.gen
import tornado.httpserver
import tornado.ioloop
from DoubanLoginAuth import DoubanOAuth2Mixin
from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/auth/login", AuthLoginHandler),
            ]
        settings = dict(
            blog_title = "test tornado blog",
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            douban_api_key='请填入api key',
            douban_api_secret='请填入api secret',
            redirect_uri='http://127.0.0.1:8000/auth/login',
            login_url="/auth/login",
            debug=True,
            )
        tornado.web.Application.__init__(self, handlers, **settings)

class HomeHandler(tornado.web.RequestHandler):
    @tornado.web.authenticated
    def get(self):
        self.write("test success")


class AuthLoginHandler(DoubanOAuth2Mixin, tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        if self.get_argument('code', False):
            user = yield self.get_authenticated_user(   # 获取到个人信息
                redirect_uri=self.settings['redirect_uri'],
                code=self.get_argument('code')
            )
            if user:
                self.write(user)
            else:
                self.write("auth error")
        else:
            yield self.authorize_redirect(
                redirect_uri=self.settings['redirect_uri'],
                client_id=self.settings['douban_api_key'],
                scope=None,
                response_type='code'
            )


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()