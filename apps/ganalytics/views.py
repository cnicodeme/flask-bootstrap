# -*- coding:utf-8 -*-

from flask import Blueprint, make_response, request, g
from functools import wraps
from ganalytics.ga import Tracker
import base64, datetime

app = Blueprint('ganalytics', __name__)

"""
Snippet:

```
<script>
var i = new Image();
i.src = 'https://api.site.com/vX/t/page.gif?' +
    'u=' + encodeURIComponent(window.location.href) +
    '&r=' + encodeURIComponent(window.document.referrer) +
    '&t=' + encodeURIComponent(window.document.title) +
    '&sr=' + encodeURIComponent(window.screen.width + 'x' + window.screen.height) +
    '&vp=' + encodeURIComponent(
        Math.max(document.documentElement.clientWidth, window.innerWidth || 0)
        + 'x' +
        Math.max(document.documentElement.clientHeight, window.innerHeight || 0)
    );
</script>
<noscript>
    <img src="https://api.site.com/vX/t/page.gif?t=<?php echo urlencode(get_the_title()); ?>" async />
</noscript>
```

Compressed:

```
<script>var i=new Image;i.src="https://api.site.com/vX/t/page.gif?u="+encodeURIComponent(window.location.href)+"&r="+encodeURIComponent(window.document.referrer)+"&t="+encodeURIComponent(window.document.title)+"&sr="+encodeURIComponent(window.screen.width+"x"+window.screen.height)+"&vp="+encodeURIComponent(Math.max(document.documentElement.clientWidth,window.innerWidth||0)+"x"+Math.max(document.documentElement.clientHeight,window.innerHeight||0));</script>
<noscript><img src="https://api.site.com/vX/t/page.gif?t=<?php echo urlencode(get_the_title()); ?>" async /></noscript>
```
"""


@app.before_app_request
def set_tracker():
    g._ga = Tracker('app')
    g._ga._load_from_request()


def pixel_response(view_func):
    """
    Return a tracking pixel response
    """
    def _decorator(*args, **kwargs):
        view_func(*args, **kwargs)
        g._ga.send()

        response = make_response(base64.b64decode('R0lGODlhAQABAID/AMDAwAAAACH5BAEAAAAALAAAAAABAAEAAAICRAEA'))
        response.headers.set('Content-Type', 'image/gif')
        response.headers.set("Cache-Control", "private, no-cache, no-cache=Set-Cookie, proxy-revalidate")
        response.headers.set("Expires", "Wed, 11 Jan 2000 12:59:00 GMT")
        response.headers.set("Last-Modified", "Wed, 11 Jan 2006 12:59:00 GMT")
        response.headers.set("Pragma", "no-cache")

        if request.cookies.get('_t') is None:
            response.set_cookie(
                '_t',
                g._ga.cid,
                expires=datetime.datetime.now() + datetime.timedelta(days=730),  # 2 years
            )
        return response

    return wraps(view_func)(_decorator)


@app.route('/page.gif')
@pixel_response
def pageview():
    g._ga.hit(
        'pageview',
        request.args.get('u', None) or request.headers.get('referer'),
        request.args.get('r', None),
        request.args.get('t', None)
    )


@pixel_response
@app.route('/event.gif')
def event():
    g._ga.event(
        request.args.get('c'),
        request.args.get('a'),
        request.args.get('l', None),
        request.args.get('v', None),
    )
