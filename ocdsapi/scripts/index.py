import plaster
import argparse
from logging import getLogger
from logging.config import fileConfig
from json import load
from elasticsearch import Elasticsearch, ElasticsearchException
from elasticsearch.helpers import bulk
from paginate_sqlalchemy import SqlalchemyOrmPage
from ocdsmerge.merge import process_schema
from ocdsapi.models import Record
from ocdsapi.utils import prepare_record, get_db_session



parser = argparse.ArgumentParser("OCDS API index builder")
parser.add_argument('config',
                    help='Path to app configuration file',
                    default='development.ini'
                    )



def main():
    args = parser.parse_args()
    fileConfig(args.config)
    logger = getLogger('ocdsapi')
    loader = plaster.get_loader(args.config, protocols=['wsgi'])
    settings = loader.get_settings('app:main')
    es = Elasticsearch([settings.get("elasticsearch.url")])
    index = settings.get("elasticsearch.index", 'releases')
    es.indices.delete(index=index, ignore=[400, 404])
    es.indices.create(index=index, ignore=400)
    mapping = settings.get("elasticsearch.mapping")
    if mapping:
        with open(mapping) as _in:
            mapping = load(_in)
            es.indices.put_mapping(
                doc_type='Tender',
                index=index,
                body=mapping
            )
    session = get_db_session(settings)
    rules = process_schema(settings.get('api.schema'))
    page = 1
    while True:
        page = SqlalchemyOrmPage(
            (session
             .query(Record)
             .order_by(Record.date.desc())),
            page,
            1000
        )
        records = []
        for record in page.items:
            record = prepare_record(
                    record,
                    [{
                        "id": r.release_id,
                        "date": r.date,
                        "ocid": r.ocid
                    } for r in record.releases],
                    rules
            )
            if record:
                records.append({
                    '_index': index,
                    '_type': 'Tender',
                    '_id': record['ocid'],
                    '_source': {'ocds': record['compiledRelease']}
                })
        try:
            resp = bulk(es, records)
            logger.info(f"Response from elasticsearch: {resp}")

        except ElasticsearchException as e:
            logger.error(f"Failed to index bulk with error: {repr(e)}")
            break
        page = page.next_page
        if not page:
            logger.info("Done indexing")
            break
