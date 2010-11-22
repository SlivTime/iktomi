# -*- coding: utf-8 -*-

__all__ = ['WSGIHandler']

import logging
import httplib
from .http import HttpException
from .core import STOP, RequestContext

logger = logging.getLogger(__name__)


def process_http_exception(response, e):
    response.status = e.status
    if e.status in (httplib.MOVED_PERMANENTLY,
                    httplib.SEE_OTHER):
        if isinstance(e.url, unicode):
            url = e.url.encode('utf-8')
        else:
            url = str(e.url)
        response.headers.add('Location', url)


class WSGIHandler(object):

    def __init__(self, app):
        self.app = app

    def status(self, number):
        return '%d %s' % (number, httplib.responses[number])

    def __call__(self, env, start_response):
        rctx = RequestContext(env)
        response = rctx.response
        try:
            result = self.app(rctx)
            if result is STOP:
                response.status = httplib.NOT_FOUND
            else:
                rctx = result
        except HttpException, e:
            process_http_exception(response, e)
        except Exception, e:
            logger.exception(e)
            raise
        headers = response.headers.items()
        start_response(response.status, headers)
        return [response.body]
