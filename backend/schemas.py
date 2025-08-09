from pydantic import BaseModel
from typing import Dict, Any
import datetime

# Ensure SQLAlchemy model instances can be serialized (orm_mode / from_attributes)
try:
	from pydantic import ConfigDict  # Pydantic v2
	_from_attrs_config = {"model_config": ConfigDict(from_attributes=True)}
except ImportError:  # Pydantic v1 fallback
	_from_attrs_config = {}

class Report(BaseModel):
	machine_id: str
	os: str
	timestamp: int
	results: Dict[str, Any]

class MachineOut(BaseModel):
	machine_id: str
	os: str
	last_checkin: datetime.datetime
	results: Dict[str, Any]
	if 'model_config' in _from_attrs_config:  # Pydantic v2
		model_config = _from_attrs_config['model_config']
	else:  # Pydantic v1 style
		class Config:
			orm_mode = True
