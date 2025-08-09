from sqlalchemy import Column, String, Integer, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Machine(Base):
	__tablename__ = "machines"
	machine_id = Column(String, primary_key=True, index=True)
	os = Column(String)
	last_checkin = Column(DateTime, default=datetime.datetime.utcnow)
	results = Column(JSON)
