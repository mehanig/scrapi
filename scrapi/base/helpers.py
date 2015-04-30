from __future__ import unicode_literals

import re
from copy import deepcopy
import functools
import six

from nameparser import HumanName

URL_REGEX = re.compile(r'(https?://\S*\.\S*)')


def single_result(l, default=''):
    if isinstance(l, list):
        l = l[0]
    if isinstance(l, six.binary_type):
        l = [l.decode(), ]
    elif isinstance(l, six.text_type):
        l = [l, ]
    return l[0] if l else default


def compose(*functions):
    '''
    evaluates functions from right to left.
    ex. compose(f, g)(x) = f(g(x))

    credit to sloria
    '''
    def inner(func1, func2):
        return lambda x: func1(func2(x))
    return functools.reduce(inner, functions)


def updated_schema(old, new):
    d = deepcopy(old)
    for key, value in new.items():
        if isinstance(value, dict) and old.get(key) and isinstance(old[key], dict):
            d[key] = updated_schema(old[key], new[key])
        else:
            d[key] = value
    return d


def default_name_parser(names):
    if isinstance(names, six.binary_type):
        names = names.decode()
    contributor_list = []
    for person in names:
        name = HumanName(person)
        if isinstance(person, six.binary_type):
            person = person.decode()
        if isinstance(name.first, six.binary_type):
            name.first = name.first.decode()
        if isinstance(name.middle, six.binary_type):
            name.middle = name.middle.decode()
        if isinstance(name.last, six.binary_type):
            name.last = name.last.decode()
        contributor = {
            'name': person,
            'givenName': name.first,
            'additionalName': name.middle,
            'familyName': name.last,
            'email': '',
            'sameAs': []
        }
        contributor_list.append(contributor)

    return contributor_list


###TODO FIX THIS IF SIX.PY2 PART!
def format_tags(all_tags, sep=','):
    tags = []
    if isinstance(all_tags, six.string_types):
        tags = all_tags.split(sep)
    elif isinstance(all_tags, six.binary_type):
        all_tags = all_tags.decode()
        tags = all_tags.split(sep)
    elif isinstance(all_tags, list):
        for tag in all_tags:
            if isinstance(tag, six.binary_type):
                tag = tag.decode()
            if sep in tag:
                tags.extend(tag.split(sep))
            else:
                tags.append(tag)
    if six.PY2:
        return list(set([unicode(tag.lower().strip()) for tag in tags if tag.strip()]))
    else:
        return list(set([six.u(tag.lower().strip()) for tag in tags if tag.strip()]))


###TODO FIX THIS IF ELSE PART.
def oai_extract_doi(identifiers):
    identifiers = [identifiers] if not isinstance(identifiers, list) else identifiers
    for item in identifiers:
        if 'doi' in item.lower():
            if six.PY2:
                return unicode(item.replace('doi:', '').replace('DOI:', '').replace('http://dx.doi.org/', '').strip())
            else:
                return six.u(item.replace('doi:', '').replace('DOI:', '').replace('http://dx.doi.org/', '').strip())
    return ''


###TODO: FIX IF six.PY2 part!!!!
def oai_extract_url(identifiers):
    identifiers = [identifiers] if not isinstance(identifiers, list) else identifiers
    for item in identifiers:
        try:
            found_url = URL_REGEX.search(item.decode()).group()
            if 'viewcontent' not in found_url:
                # if six.PY2:
                return found_url.decode('utf-8')
                # else:
                #     return found_url.decode('utf-8')
        except AttributeError:
            continue


def oai_process_contributors(*args):
    names = []
    for arg in args:
        if isinstance(arg, list):
            for name in arg:
                names.append(name)
        elif arg:
            names.append(arg)
    return default_name_parser(names)


def pack(*args, **kwargs):
    return args, kwargs


def data_to_unicode(data):
    if isinstance(data, six.binary_type):
        return data.decode()
    elif isinstance(data, six.string_types):
        return data
    else:
        raise TypeError