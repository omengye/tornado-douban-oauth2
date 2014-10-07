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
            (r"/auth/logout", AuthLogoutHandler),
            ]
        settings = dict(
            blog_title = "test tornado blog",
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            douban_api_key='请填入api key',
            douban_api_secret='请填入api secret',
            redirect_uri='http://127.0.0.1:8000/auth/login',
            login_url="/auth/login",
            cookie_secret="bZBc2sEbQLKqv7GkJD/VB8YuTC3eC0R0kRvJ5/xX37P=",
            xsrf_cookies=True,
            debug=True,
            )
        tornado.web.Application.__init__(self, handlers, **settings)

class BaseHandle(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user_id")

class HomeHandler(BaseHandle):
    @tornado.web.authenticated
    def get(self):
        self.write("Auth Success <br> welcome " + self.current_user + "!")

class AuthLogoutHandler(BaseHandle):
    def get(self):
        self.clear_cookie("user_id")
        self.redirect(self.get_argument("next", "/"))

class AuthLoginHandler(DoubanOAuth2Mixin, tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        if self.get_argument('code', False):
            user = yield self.get_authenticated_user(   # 获取到个人信息
                redirect_uri=self.settings['redirect_uri'],
                code=self.get_argument('code')
            )
            if user:
                self.set_secure_cookie("user_id", str(user['uid']))
                self.redirect(self.get_argument("next", "/"))
        else:
            yield self.authorize_redirect(
                redirect_uri=self.settings['redirect_uri'],
                client_id=self.settings['douban_api_key'],
                scope=None, # 使用默认的scope权限
                response_type='code'
            )


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()