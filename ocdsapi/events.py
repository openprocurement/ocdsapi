class RecordBatchUpdate:
    """ Event generated each time when record is created/update with new release """
    def __init__(self, request, records):
        self.request = request
        self.records = records
