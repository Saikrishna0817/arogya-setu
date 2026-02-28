"""SQLAlchemy models for the vault database."""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from config.paths import Paths

Base = declarative_base()

# Association table
patient_prescription_association = Table(
    'patient_prescriptions',
    Base.metadata,
    Column('patient_id', Integer, ForeignKey('patients.patient_id')),
    Column('prescription_id', Integer, ForeignKey('prescriptions.id'))
)


class Prescription(Base):
    __tablename__ = 'prescriptions'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.patient_id'))
    image_path = Column(Text)
    raw_ocr = Column(Text)
    parsed_json = Column(Text)  # JSON string
    explanation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tags = Column(Text)
    
    patient = relationship("Patient", back_populates="prescriptions")


class Patient(Base):
    __tablename__ = 'patients'
    
    patient_id = Column(Integer, primary_key=True)
    name = Column(String(255))
    age = Column(Integer)
    gender = Column(String(20))
    allergies = Column(Text)  # JSON string
    conditions = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    
    prescriptions = relationship("Prescription", back_populates="patient")


def get_engine():
    """Create database engine."""
    db_path = Paths.VAULT_DB
    return create_engine(f'sqlite:///{db_path}')


def init_db():
    """Initialize all tables."""
    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine


def get_session():
    """Get database session."""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()