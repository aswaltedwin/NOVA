from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import Config

Base = declarative_base()

class Job(Base):
    __tablename__ = 'jobs'
    
    id = Column(String, primary_key=True)
    status = Column(String, default='pending')
    progress = Column(Integer, default=0)
    risk_score = Column(Integer, default=0) # New: Numerical risk score
    model = Column(String)

    log_input = Column(Text)
    intermediate_results = Column(Text, nullable=True)
    result = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = Column(String, default="Nocturnal_Analyst") # Default for current version
    action = Column(String)
    details = Column(Text)
    source_ip = Column(String, nullable=True)

# Database Engine Setup
engine = create_engine(Config.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
