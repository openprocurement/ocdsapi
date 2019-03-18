from sqlalchemy import (
    Column,
    Index,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    TIMESTAMP
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from .meta import Base


class Release(Base):

    __tablename__ = 'releases'

    id = Column(String, primary_key=True)
    ocid = Column(String, ForeignKey('records.id'))
    date = Column(String)
    timestamp = Column(TIMESTAMP)

    value = Column(JSONB)


class Record(Base):
    __tablename__ = 'records'
    id = Column(String, primary_key=True)
    date = Column(String)
    timestamp = Column(TIMESTAMP)

    compiled_release = Column(JSONB)
    releases = relationship(
        "Release",
        backref='record',
        lazy='joined',
    )


Index('ocids', Release.ocid)
Index('date', Release.date.desc())
Index('date-record', Record.id, Record.date.desc())
Index('release-timestamp', Release.timestamp)
Index('record-timestamp', Record.timestamp)
Index('record-timestamp-id', Record.timestamp.asc(), Record.id)
