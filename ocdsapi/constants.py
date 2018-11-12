import json
import os.path

here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, 'data', 'release-package-schema.json')) as _in:
    release_package_schema = json.load(_in)
with open(os.path.join(here, 'data', 'record-package-schema.json')) as _in:
    record_package_schema = json.load(_in)



YES = frozenset(('true', '1', 'y', 'yes', 't'))
SWAGGER = {
    'title': 'OCDS API',
    'description': 'This OCDS API is built based on Version 1.1  of OCDS that  provides a scheme for publishing releases and records about contracting processes. The OCDS API helps to  make  contracting processes more transparent and accountable by providing a comprehensive, filterable OCDS data library. It supports publication of multiple releases and records in bulk ‘packages’, or as individual files, accessible at their own URIs and it returns data in an easily interpretable and scrapable JSON format.',
    'version': '1.1',
    'termsOfService': ''
}
DESCRIPTIONS = {
    "releases.json": {

        "get": {
        "responses": {
            "200": {"description": "Release package"},
            "404": {"description": "Release package unavailable"}
        },
        "parameters": [
            {
            "in": "query",
            "name": "idsOnly",
            "type": "string",
            "description": "A list of objects is returned but contiains only the 'ocid' and 'id' properties. Useful for large datasets where you just want to see what new records ther are."
            },
            {
            "in": "query",
            "name": "page",
            "type": "string",
            "description": "Ask for a specific page or results if server has paging"
            }
            ]
        }
    },
    "release.json": {
        "get": {

            "description" : "An OSDS release object can be returned. Sometimes, a user’s release ID for an API may be duplicated by chance. In such instance the user has to know either a package URL or OC ID and therefore obtain an individual release ID. It is mandatory for each release to comprise such information as an OC ID, a unique release ID, a release tag and any other characteristics of the event to be provided to the users",
            "responses": {
                "200": {"description": "Single Release"},
                "404": {"description": "Release with provided releaseID does not exists"}
            },
            "parameters": [
            {
                "in": "query",
                "name": "releaseID",
                "required": True,
                "type": "string",
                "description": "The release id of the release"
            }
            ]
        },
    },
    "record.json": {
        "get": {
            "description" : "This is an OCDS record object supplying a snapshot of the running state of the contracting process where he information from all the preceding releases is brought together. As soon as new information is introduced, it gets updated. At least one record must be present for each contracting process in order to furnish a full list of releases associated with this contracting process",
            "responses": {
                "200": {"description": "Single Record"},
                "404": {"description": "Record with provided ocid does not exists"}
            },
            "parameters": [
            {
                "in": "query",
                "name": "ocid",
                "required": True,
                "type": "string",
                "description": "The ocid of the record"
            }
            ]
        }
    },
    "records.json": {
        "get": {
        "description" : "This returns an object with a list of OCDS records and a links object. The records embrace all the information related to the contracting process and provide a snapshot view of its current state. These records also include a versioned history of changes that were made step by step. Only one record is possible for each contracting process, created when the releases are merged. ‘Next’ property pertaining to links object should contain the URL of the next page to be visited when scanning the results. The ‘records’ list usually contains a complete OCDS record. The search results are to be listed by modification date in descending order.",
        "responses": {
            "200": {"description": "List of records"},
            "404": {"description": "Release package unavailable"}
        },
        "parameters": [
        {
            "in": "query",
            "name": "idsOnly",
            "type": "string",
            "description": "A list of objects is returned but contiains only the 'ocid' and 'id' properties. Useful for large datasets where you just want to see what new records ther are."
        },
        {
            "in": "query",
            "name": "page",
            "type": "string",
            "description": "Ask for a specific page or results if server has paging"
        }
        ]
    }}
}
RESPONSES = {
    "releases.json": {
        "get": {
            'schema': release_package_schema
        }
    },
    "release.json": {
        "get": {
            'schema': release_package_schema
        },
    },
    "record.json": {
        "get": {
            'schema': record_package_schema
        },
    },
    "records.json": {
        "get": {
            'schema': record_package_schema
        },
    }
}