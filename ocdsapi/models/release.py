from sqlalchemy import (
    Column,
    Index,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from .meta import Base


class Release(Base):

    __tablename__ = 'releases'

    release_id = Column(String, primary_key=True)
    ocid = Column(String, ForeignKey('records.ocid'))
    date = Column(String)
    last_published = Column(DateTime)
    value = Column(JSON)


class Record(Base):
    __tablename__ = 'records'
    ocid = Column(String, primary_key=True)
    date = Column(String)
    compiled_release = Column(JSON)

    releases = relationship(
        "Release",
        backref='record',
        lazy='joined'
    )


Index('ocids', Release.ocid)
Index('date', Release.date.desc())
Index('date-record', Record.ocid, Record.date.desc())