from logging import getLogger
from ocdsapi.utils import prepare_record
from elasticsearch.helpers import bulk, ElasticsearchException


logger = getLogger('ocdsapi')


def reindex_record_bulk(event):
    request = event.request
    index_bulk = [{
        '_index': request.registry.es_index,
        '_type': 'Tender',
        '_id': es_doc.id,
        '_source': {'ocds': es_doc.compiled_release}
        } for es_doc in event.records
    ]
    try:
        bulk(request.registry.es, index_bulk)
        logger.info(f"Indexed to elasticsearch {len(index_bulk)}")
    except ElasticsearchException as e:
        logger.error("Failed to index records to elasticsearch")

