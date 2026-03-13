from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    Date,
    JSON
)
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import VECTOR
from config import EMBEDDING_DIM

Base = declarative_base()


class Audit(Base):
    __tablename__ = "audits"

    id = Column(Integer, primary_key=True)
    audit_name = Column(String(150))
    audit_type = Column(String(20))
    start_date = Column(Date)
    end_date = Column(Date)

    faults = relationship("Fault", back_populates="audit")


class Fault(Base):
    __tablename__ = "faults"

    id = Column(Integer, primary_key=True)
    audit_id = Column(Integer, ForeignKey("audits.id"))
    date = Column(Date)
    asset = Column(Text)
    building = Column(String(100))
    fault_type = Column(String(100))
    message = Column(Text)

    cluster_id = Column(Integer)
    embedding = Column(JSON)
    "embedding = Column(VECTOR(EMBEDDING_DIM))"
    image_path = Column(String) 
    audit = relationship("Audit", back_populates="faults")