from sqlalchemy import (
    Column,
    Index,
    Integer,
    String,
    DateTime,
    Boolean,
)
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB
from .meta import Base


class Release(Base):

    __tablename__ = 'releases'

    release_id = Column(String, primary_key=True)
    ocid = Column(String)
    date = Column(DateTime)
    in_static = Column(Boolean, default=False)
    value = Column(JSONB)


Index('ocids', Release.ocid)
Index('ids', Release.release_id)
Index('unreleased', Release.in_static, postgresql_where=Release.in_static==False)
Index('date_released', Release.date)
