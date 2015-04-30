from datetime import datetime

import pytz
import six

def timestamp():
    return six.u(pytz.utc.localize(datetime.utcnow()).isoformat())

def copy_to_unicode(element, encoding='utf-8'):
    """ used to transform the lxml version of unicode to a
    standard version of unicode that can be pickalable -
    necessary for linting """

    element = ''.join(element)
    if isinstance(element, six.text_type):
        return element
    else:
        return unicode(element, encoding=encoding)
        # return six.u(element)

def stamp_from_raw(raw_doc, **kwargs):
    kwargs['normalizeFinished'] = timestamp()
    stamps = raw_doc['timestamps']
    stamps.update(kwargs)
    return stamps