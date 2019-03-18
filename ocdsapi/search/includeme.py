from elasticsearch import Elasticsearch
from ocdsapi.search.subscribers import reindex_record_bulk
from ocdsapi.events import RecordBatchUpdate

import logging
import json


logger = logging.getLogger(__name__)


def includeme(config):
    settings = config.get_settings()
    elasticsearch = settings.get("elasticsearch.url")
    es = Elasticsearch([elasticsearch])
    index = settings.get("elasticsearch.index", 'releases')
    config.registry.es = es
    config.registry.es_index = index
    es.indices.create(index=index, ignore=400)
    logger.info(f"Created index {index}")
    mapping_ = settings.get("elasticsearch.mapping")
    if mapping_:
        with open(mapping_) as _in:
            mapping = json.load(_in)
            try:
                es.indices.put_mapping(
                    doc_type='Tender',
                    index=index,
                    body=mapping
                    )
                logger.info(f"Updated mapping for elasticsearch {mapping_}")
            except Exception as e:
                logger.warn(f"Failed to update elasticsearch mapping with error: {e}")
    config.add_subscriber(reindex_record_bulk, RecordBatchUpdate)
