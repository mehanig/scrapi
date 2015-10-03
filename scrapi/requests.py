"""A wrapper around requests that records all requests made with it.
    Supports get, put, post, delete and request
    all calls return an instance of HarvesterResponse
"""
from __future__ import absolute_import

import json
import time
import logging
import functools

import six
import furl
import requests

from scrapi import events
from scrapi import settings
from scrapi.processing import HarvesterResponse


logger = logging.getLogger(__name__)


def _maybe_load_response(method, url):
    try:
        return HarvesterResponse.get(url=url.lower(), method=method)
    except HarvesterResponse.DoesNotExist:
        return None


def record_or_load_response(method, url, throttle=None, force=False, params=None, expected=(200,), **kwargs):

    resp = _maybe_load_response(method, url)

    if not force and resp and resp.ok:
        logger.info('Return recorded response from "{}"'.format(url))
        return resp

    if force:
        logger.warning('Force updating request to "{}"'.format(url))
    else:
        logger.info('Making request to "{}"'.format(url))

    maybe_sleep(throttle)

    response = requests.request(method, url, **kwargs)

    if not response.ok:
        events.log_to_sentry('Got non-ok response code.', url=url, method=method)

    if isinstance(response.content, six.text_type):
        response.content = response.content.encode('utf8')

    if not resp:
        return HarvesterResponse(
            url=url.lower(),
            method=method,
            ok=response.ok,
            content=response.content,
            encoding=response.encoding,
            status_code=response.status_code,
            headers_str=json.dumps(dict(response.headers))
        ).save()

    logger.warning('Skipped recorded response from "{}"'.format(url))

    return resp.update(
        ok=(response.ok or response.status_code in expected),
        content=response.content,
        encoding=response.encoding,
        status_code=response.status_code,
        headers_str=json.dumps(dict(response.headers))
    ).save()


def maybe_sleep(sleepytime):
    # exists so that this alone can be mocked in tests
    if sleepytime:
        time.sleep(sleepytime)


def request(method, url, params=None, **kwargs):
    """Make a recorded request or get a record matching method and url

    :param str method: Get, Put, Post, or Delete
    :param str url: Where to make the request to
    :param bool force: Whether or not to force the new request to be made
    :param int throttle: A time in seconds to sleep before making requests
    :param dict kwargs: Addition keywords to pass to requests
    """
    if params:
        url = furl.furl(url).set(args=params).url
    logger.info(url)
    if settings.RECORD_HTTP_TRANSACTIONS:
        return record_or_load_response(method, url, **kwargs)

    logger.info('Making request to "{}"'.format(url))
    throttle = kwargs.pop('throttle', 0)
    maybe_sleep(throttle)
    # Need to prevent force from being passed to real requests module
    kwargs.pop('force', None)
    return requests.request(method, url, **kwargs)


get = functools.partial(request, 'get')
put = functools.partial(request, 'put')
post = functools.partial(request, 'post')
delete = functools.partial(request, 'delete')
