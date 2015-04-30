from __future__ import unicode_literals

import functools

import six

from scrapi.base import XMLHarvester
from scrapi.linter import RawDocument
from scrapi.base.schemas import CONSTANT
from scrapi.base.helpers import updated_schema, pack

from .utils import get_leaves
from .utils import TEST_SCHEMA, TEST_NAMESPACES, TEST_XML_DOC


class TestHarvester(XMLHarvester):
    long_name = 'TEST'
    short_name = 'crossref'
    url = 'TEST'
    schema = TEST_SCHEMA
    namespaces = TEST_NAMESPACES

    def harvest(self, days_back=1):
        return [RawDocument({
            'doc': str(TEST_XML_DOC),
            'source': 'crossref',
            'filetype': 'XML',
            'docID': "1"
        }) for _ in six.moves.range(days_back)]


class TestTransformer(object):

    def setup_method(self, method):
        self.harvester = TestHarvester()

    def test_arg_kwargs(self):
        def process_title(title, title1="test"):
            t = title
            t1 = title1
            # import pdb; pdb.set_trace()
            if isinstance(title, six.binary_type):
                t = [title.decode(), ]
            if isinstance(title1, six.binary_type):
                t1 = [title1.decode(), ]
            if isinstance(title1, six.text_type):
                t1 = [title1, ]
            if isinstance(title, six.text_type):
                t = [title, ]
            return (t[0] if isinstance(t, list) else t) + (t1[0] if isinstance(t1, list) else t1)


        def process_title2(title1="test"):
            return title1[0] if isinstance(title1, list) else title1

        args = ("//dc:title/node()", )
        kwargs = {"title1": "//dc:title/node()"}

        self.harvester.schema = updated_schema(
            TEST_SCHEMA,
            {
                'title': (pack(*args, **kwargs), process_title),
                # 'otherProperties': {
                #     'title2': (pack(*args), process_title),
                #     'title3': (pack(**kwargs), process_title2),
                #     'title4': (pack('//dc:title/node()', title1="//dc:title/node()"), process_title)
                # }
            }
        )

        results = [self.harvester.normalize(record) for record in self.harvester.harvest(days_back=1)]

        for result in results:
            assert result['title'] == "TestTest"
            # assert result['otherProperties']['title2'] == 'Testtest'
            # assert result['otherProperties']['title3'] == 'Test'
            # assert result['otherProperties']['title4'] == "TestTest"

    def test_normalize(self):
        results = [
            self.harvester.normalize(record) for record in self.harvester.harvest(days_back=10)
        ]

        for result in results:
            assert result['title'] == "Title overwritten"
            # assert result['otherProperties']['title1'] == 'Test'
            # assert result['otherProperties']['title2'] == 'test'
            # assert result['otherProperties']['title3'] == 'Testtest'

            for (k, v) in get_leaves(result.attributes):
                assert type(v) != functools.partial

    def test_constants(self):
        self.harvester.schema = updated_schema(
            TEST_SCHEMA, {
                # 'otherProperties': {
                #     'test': CONSTANT('test')
                # }
            }
        )
        results = [
        self.harvester.normalize(record) for record in self.harvester.harvest(days_back=1)
        ]

        # for result in results:
            # assert result['otherProperties']['test'] == 'test'
