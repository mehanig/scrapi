from sqlalchemy import create_engine
from sqlalchemy import Table, Column, String, MetaData

from scrapi.processing.base import BaseProcessor


class PostgreSQLProcessor(BaseProcessor):
    NAME = 'postgres'

    def __init__(self):
        self.engine = create_engine('postgresql://fabian@localhost:5432/postgres')
        self.set_schema()


    def process_normalized(self, raw_doc, normalized):
        raise NotImplementedError

    def process_raw(self, raw_doc):
        ins = self.raw.insert().values(
            docID=raw_doc['docID'],
            source=raw_doc['source'],
            doc=raw_doc['doc'],
            filetype=raw_doc['filetype']
        )
        conn = self.engine.connect()
        result = conn.execute(ins)

    def set_schema(self):
        metadata = MetaData()
        self.raw = Table('raw2', metadata,
            Column('docID', String, primary_key=True),
            Column('doc', String),
            Column('source', String),
            Column('filetype', String)
        )
        metadata.create_all(self.engine)
