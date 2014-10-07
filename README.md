#tornado douban oauth2
tornado douban oauth2 基于tornado的douban oauth2认证，支持最新的tornado 4.0.2，采用了gen.coroutine异步，主要参照了tornado.auth的第三方认证（如 google，facebook）而写。  
附豆瓣的[Oauth2](http://developers.douban.com/wiki/?title=oauth2)，以及[tornado.auth](http://tornado.readthedocs.org/en/latest/auth.html)  
**使用说明**  
首先需要填入自己申请的豆瓣api key和secret  
打开http://127.0.0.1:8000/由于self.get_current_user值为空，会直接跳转到http://127.0.0.1:8000/auth/login/，而由于采用了douban oauth2的认证方式，故会继续跳转到豆瓣的验证页面，登陆成功后会自动用获取到的access_token去获取用户的个人信息，其中uid为用户名，将uid设置到cookie。tornado采用了self.redirect(self.get_argument('next', '/'))，通过next来跳转到'/'页面。另，打开http://127.0.0.1:8000/auth/logout/会清空cookie。