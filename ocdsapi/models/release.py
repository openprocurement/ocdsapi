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

    id = Column(String, primary_key=True)
    ocid = Column(String)
    date = Column(DateTime)
    released = Column(Boolean, default=False)
    value = Column(JSONB)


Index('ocids', Release.ocid)
Index('unreleased', Release.released, postgresql_where=Release.released==False)
Index('date_released', Release.date)
