from __future__ import unicode_literals

import abc
import logging

from jsonpointer import resolve_pointer, JsonPointerException

import six

logger = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class BaseTransformer(object):

    @abc.abstractmethod
    def _transform_string(self, string, doc):
        raise NotImplementedError

    @abc.abstractproperty
    def schema(self):
        raise NotImplementedError

    def transform(self, doc):
        return self._transform(self.schema, doc)

    def _transform(self, schema, doc):
        transformed = {}
        for key, value in schema.items():
            if isinstance(value, dict):
                transformed[key] = self._transform(value, doc)
            elif isinstance(value, list) or isinstance(value, tuple):
                transformed[key] = self._transform_iterable(value, doc)
            elif isinstance(value, six.string_types):
                transformed[key] = self._transform_string(value, doc)
            elif isinstance(value, six.binary_type):
                transformed[key] = self._transform_string(value.decode('utf_8'), doc)
            elif callable(value):
                transformed[key] = value(doc)
        return transformed

    def _transform_iterable(self, l, doc):

        if isinstance(l[0], tuple) and len(l) == 2:
            return self._transform_args_kwargs(l, doc)

        fn, values = l[-1], l[:-1]
        args = []

        for value in values:
            if isinstance(value, six.string_types):
                args.append(self._transform_string(value, doc))
            elif isinstance(value, six.binary_type):
                args.append(self._transform_string(value.decode('utf_8'), doc))
            elif callable(value):
                args.append(value(doc))
        return fn(*args)

    def _transform_args_kwargs(self, l, doc):
        fn = l[1]
        return fn(
            *self._transform_args(l[0], doc),
            **self._transform_kwargs(l[0], doc)
        )

    def _transform_args(self, t, doc):
        return [self._transform_string(arg, doc) for arg in t[0]]

    def _transform_kwargs(self, t, doc):
        return {
            k: self._transform_string(v, doc) for k, v in t[1].items()
        } if len(t) == 2 else {}


@six.add_metaclass(abc.ABCMeta)
class XMLTransformer(BaseTransformer):

    def _transform_string(self, string, doc):
        val = doc.xpath(string, namespaces=self.namespaces)
        return six.u(val[0].encode('utf_8')) if len(val) == 1 else [six.u(v.encode('utf_8')) for v in val] or ''

    @abc.abstractproperty
    def namespaces(self):
        raise NotImplementedError


@six.add_metaclass(abc.ABCMeta)
class JSONTransformer(BaseTransformer):

    def _transform_string(self, val, doc):
        try:
            return resolve_pointer(doc, val)
        except JsonPointerException:
            return ''