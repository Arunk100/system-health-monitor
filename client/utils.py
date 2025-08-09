import os
import platform
import uuid
import json

def get_machine_id():
	# Use a persistent UUID per machine
	id_file = os.path.expanduser("~/.system_health_id")
	if os.path.exists(id_file):
		with open(id_file, "r") as f:
			return f.read().strip()
	else:
		machine_id = str(uuid.uuid4())
		with open(id_file, "w") as f:
			f.write(machine_id)
		return machine_id

def load_last_report():
	try:
		with open("last_report.json", "r") as f:
			return json.load(f)
	except Exception:
		return None

def save_last_report(data):
	with open("last_report.json", "w") as f:
		json.dump(data, f)
