import arrow
import couchdb
import logging
from multiprocessing import Value
from datetime import timedelta, datetime, timezone
from iso8601 import parse_date
from couchdb.design import ViewDefinition
from ocdsapi.utils import prepare_responce_doc
from repoze.lru import lru_cache, LRUCache
from .paginate import PaginationHelper
from gevent import pool, spawn, sleep
from time import time



releases_ocid = ViewDefinition(
    'releases', 'id_index',
    map_fun=u"""function(doc) {emit([doc._id, doc.ocid], doc.date);}"""
)

releases_id = ViewDefinition(
    'releases', 'date_index',
    map_fun=u"""function(doc) {emit([doc.date, doc._id], doc.ocid);}"""
)
LOGGER = logging.getLogger("")
WATCHER = Value('i', 0)
DAY = 86400


class ReleaseStorage(object):

    def __init__(self, host, port, db_name, cache=None):
        server = couchdb.Server("http://{}:{}".format(host,
                                                      port))
        if db_name in server:
            self.db = server[db_name]
        else:
            self.db = server.create(db_name)

        ViewDefinition.sync_many(
            self.db,
            [releases_ocid, releases_id]
            )
        LOGGER.info("Starting storage: {}".format(
            self.db.info()
        ))
        if cache:
            LOGGER.warn("Starting caching")
            self.cache = LRUCache(cache)
            self._inside = lru_cache(maxsize=cache, cache=self.cache)(self._inside)
            self.build_cache()
            with WATCHER.get_lock():
                if WATCHER.value == 0:
                    self.w = spawn(self.watcher)
                    WATCHER.value = 1

    def watcher(self):
        """cache updater
        """
        sleep(DAY)
        while 1:
            self.cache.clear()
            LOGGER.info("Cache invalidated. Started to build new")
            self.build_cache()
            sleep(DAY)

    def build_cache(self):

        def cache_page(start, end):
            LOGGER.debug("Caching page {} -- {}".format(start, end))
            self._inside(start, end)

        min_date = self.min_date()
        _pool = pool.Pool(200)
        delta = timedelta(days=1)
        while arrow.get(min_date).datetime < datetime.now(timezone.utc):
            next_date = PaginationHelper.format(
                arrow.get(min_date) + delta
                )
            _pool.spawn(cache_page, min_date, next_date)
            min_date = next_date
        _pool.join()
        LOGGER.info("Caching done")
        LOGGER.info(
            "Cache size: {} items".format(len(self.cache.data))
        )

    def _by_id(self, startkey, endkey):
        responce = self.db.view(
            'releases/id_index',
            startkey=startkey,
            endkey=endkey,
            include_docs=True,
            limit=1,
            )
        if responce.rows:
            for row in responce.rows:
                doc = row.get('doc')
                if doc:
                    return prepare_responce_doc(doc)
        return ""

    def get_id(self, id):
        startkey = (id, '')
        endkey = (id, 'xxxxxxxxxxx')
        return self._by_id(startkey, endkey)

    def get_ocid(self, ocid):
        startkey = ('', ocid)
        endkey = ('x' * 33, ocid)
        return self._by_id(startkey, endkey)

    def _by_date(self, **kw):
        for item in self.db.view(
                'releases/date_index',
                **kw
                ):
            key = item.get('key')
            if key:
                return arrow.get(key[0]).format("YYYY-MM-DD")
    
    def min_date(self):
        return self._by_date(limit=1)
        
    def max_date(self):
        return self._by_date(
            limit=1,
            descending=True
            )

    def get_window(self):
        return (self.min_date(), self.max_date())
    
    def _inside(self, start_date, end_date):
        return self.db.view(
            'releases/date_index',
            startkey=(parse_date(start_date).isoformat(), ""),
            endkey=(parse_date(end_date).isoformat(), ""),
            )

    def ids_inside(self, start_date="", end_date=""):
        return [
            item.get('key')[1]
            if item else ""
            for item in self._inside(start_date, end_date)
        ]

    def ocids_inside(self, start_date, end_date):
        return [
            row.value
            for row in self._inside(start_date, end_date)
        ]