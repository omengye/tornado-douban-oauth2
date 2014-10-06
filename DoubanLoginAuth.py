# -*- coding: utf-8 -*-
import tornado.httputil
import tornado.httpclient
import tornado.web
import tornado.gen
from tornado.auth import AuthError
import urllib
from tornado.concurrent import return_future
from tornado.auth import _auth_return_future
from tornado import escape
import functools

class DoubanMixin(object):
    @return_future
    def authorize_redirect(self, redirect_uri=None, client_id=None,
                           client_secret=None, extra_params=None,
                           callback=None, scope=None, response_type="code"):
        args = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': response_type
        }
        if scope:
            args['scope'] = ' '.join(scope)

        self.redirect(
            tornado.httputil.url_concat(self._OAUTH_AUTHORIZE_URL, args))   #跳转到认证页面
        callback()

    def _oauth_request_token_url(self, redirect_uri=None, client_id=None, client_secret=None, code=None):
        url = self._OAUTH_ACCESS_TOKEN_URL
        args = dict(
            client_id=client_id,
            redirect_uri=redirect_uri,
            client_secret=client_secret,
            grant_type="authorization_code",
            code=code
        )
        return tornado.httputil.url_concat(url, args)

class DoubanOAuth2Mixin(DoubanMixin):
    _OAUTH_ACCESS_TOKEN_URL = 'https://www.douban.com/service/auth2/token'
    _OAUTH_AUTHORIZE_URL = 'https://www.douban.com/service/auth2/auth?'

    def get_auth_http_client(self):
        return tornado.httpclient.AsyncHTTPClient()

    @_auth_return_future
    def get_authenticated_user(self, redirect_uri, code, callback):
        http = self.get_auth_http_client()
        body = urllib.urlencode({
            'redirect_uri': redirect_uri,
            'code': code,
            'client_id': self.settings['douban_api_key'],
            'client_secret': self.settings['douban_api_secret'],
            "grant_type": "authorization_code",
            })

        http.fetch(self._OAUTH_ACCESS_TOKEN_URL, functools.partial(self._on_access_token, callback),
                   method="POST", body=body)

    def _on_access_token(self, future, response):
        if response.error:
            future.set_exception(AuthError('Douban Auth Error: %s' % str(response)))
            return
        args = escape.json_decode(response.body)
        # future.set_result(args)
        self.get_user_info(access_token=args['access_token'],
                           callback=functools.partial(self._on_get_user_info, future))

    def _on_get_user_info(self, future, user):
        if user is None:
            future.set_result(None)
            return
        future.set_result(user)

    @_auth_return_future
    def get_user_info(self, access_token, callback):
        url = 'https://api.douban.com/v2/user/~me'
        http = tornado.httpclient.AsyncHTTPClient()
        req = tornado.httpclient.HTTPRequest(url, headers={"Authorization":"Bearer " + access_token})
        http.fetch(req, functools.partial(self._on_get_user_request, callback))

    def _on_get_user_request(self, future, response):
        if response.error:
            future.set_exception(AuthError('Error response fetching',
                                           response.error, response.request.url))
            return
        future.set_result(escape.json_decode(response.body))
