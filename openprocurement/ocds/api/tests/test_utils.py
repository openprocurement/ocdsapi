from iso8601 import parse_date
from openprocurement.ocds.api.utils import (
    form_next_date,
    form_record,
    filter_id_rev
)


def test_form_mext_date():
    start_date = '2017-01-01'
    result = form_next_date(start_date)
    assert len(result) == 2
    assert (parse_date(result[1]) - parse_date(start_date)).days == 1
    page = 5
    result = form_next_date(start_date, page=page)
    assert len(result) == 3
    assert (parse_date(result[0]) - parse_date(start_date)).days == page
    assert (parse_date(result[1]) - parse_date(start_date)).days == page + 1
    assert (parse_date(result[2]) - parse_date(start_date)).days == page - 1


def test_compile_releases():
    release = {"id": "test", "ocid": "test1",
               "date": "2017-01-01", "tender": {"id": "test"}}
    record = form_record(release)
    for key in ['compiledRelease', 'releases', 'ocid']:
        assert key in record


def test_filter_id_rev():
    doc = {'id': "test", "_id": "test", "_rev": "test"}
    filtered = filter_id_rev(doc)
    assert "_id" not in filtered
    assert "_rev" not in filtered
    assert "id" in filtered
