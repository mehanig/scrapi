from riak import RiakClient, RiakNode

from scrapi.processing.base import BaseProcessor


class RiakProcessor(BaseProcessor):
    NAME = 'riak'

    def __init__(self):
        self.client = RiakClient()
        self.bucket = self.client.bucket("scrapi")

    def process_normalized(self, raw_doc, normalized):
        raise NotImplementedError

    def process_raw(self, raw_doc):
        docID = raw_doc['source'] + '_' + raw_doc['docID']
        doc = self.bucket.get(docID)
        if doc.data:
            doc.data = raw_doc['doc']
            doc.store()
        else:
            self.bucket.new(key=docID, data=raw_doc['doc'], content_type='application/{}'.format(raw_doc['filetype'])).store()

if __name__ == '__main__':
    p = RiakProcessor()
    b = p.client.bucket('test')
    key = b.new('one', data=1)
    key.store()
    print b.get('two').data
