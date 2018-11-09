from sqlalchemy import (
    Column,
    Index,
    Integer,
    String,
    DateTime,
    Boolean,
)
from sqlalchemy.dialects.postgresql import JSON
from .meta import Base


class Release(Base):

    __tablename__ = 'releases'

    release_id = Column(String, primary_key=True)
    ocid = Column(String)
    date = Column(DateTime)
    in_static = Column(Boolean, default=False)
    value = Column(JSON)

Index('ocids', Release.ocid)
Index('unreleased', Release.in_static, postgresql_where=Release.in_static==False)