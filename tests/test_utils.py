from ocdsapi.utils import (
    prepare_responce_doc
)


def test_prepare_response_doc():
    doc = {'id': "test", "_id": "test", "_rev": "test"}
    filtered = prepare_responce_doc(doc)
    assert "_id" not in filtered
    assert "_rev" not in filtered
    assert "id" in filtered
