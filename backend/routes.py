from fastapi import APIRouter, Depends, HTTPException, Header, Response
from sqlalchemy.orm import Session
from database import get_db
from models import Machine
from config import API_KEY
from schemas import Report, MachineOut
import datetime

router = APIRouter()

@router.post("/report")
def report_status(report: Report, db: Session = Depends(get_db), x_api_key: str | None = Header(default=None, alias="X-API-Key")):
	if API_KEY and x_api_key != API_KEY:
		raise HTTPException(status_code=401, detail="Invalid API key")
	machine = db.query(Machine).filter(Machine.machine_id == report.machine_id).first()
	if machine:
		machine.os = report.os
		machine.last_checkin = datetime.datetime.utcfromtimestamp(report.timestamp)
		machine.results = report.results
	else:
		machine = Machine(
			machine_id=report.machine_id,
			os=report.os,
			last_checkin=datetime.datetime.utcfromtimestamp(report.timestamp),
			results=report.results,
		)
		db.add(machine)
	db.commit()
	return {"ok": True}

@router.get("/machines", response_model=list[MachineOut])
def list_machines(db: Session = Depends(get_db), os: str = None, issues: bool = False):
	q = db.query(Machine)
	if os:
		q = q.filter(Machine.os == os)
	rows = q.all()
	if issues:
		filtered = []
		for m in rows:
			res = m.results or {}
			# Determine issue: disk not encrypted (status False), update not up_to_date False, antivirus not enabled, sleep > 10
			issue = False
			try:
				de = res.get('disk_encryption', {})
				if isinstance(de, dict):
					if de.get('status') is False and not de.get('skipped'): issue = True
				elif de is False:
					issue = True
				os_up = res.get('os_update', {})
				if isinstance(os_up, dict) and os_up.get('up_to_date') is False and not os_up.get('skipped'): issue = True
				av = res.get('antivirus', {})
				if isinstance(av, dict) and (av.get('present') is False or av.get('enabled') is False) and not av.get('skipped'): issue = True
				slp = res.get('inactivity_sleep', {})
				if isinstance(slp, dict):
					mins = slp.get('sleep_minutes')
					if mins is not None and mins > 10: issue = True
			except Exception:
				pass
			if issue:
				filtered.append(m)
		rows = filtered
	return rows

@router.get("/machines.csv")
def machines_csv(db: Session = Depends(get_db), os: str = None, issues: bool = False):
	rows = list_machines(db=db, os=os, issues=issues)
	# Build CSV manually
	headers = ["machine_id","os","last_checkin","disk_encrypted","os_up_to_date","antivirus_ok","sleep_minutes"]
	lines = [",".join(headers)]
	for m in rows:
		res = m.results or {}
		de = res.get('disk_encryption', {})
		if isinstance(de, dict):
			disk_ok = de.get('status')
		else:
			disk_ok = de
		os_up = res.get('os_update', {})
		if isinstance(os_up, dict):
			up_ok = os_up.get('up_to_date')
		else:
			up_ok = os_up
		av = res.get('antivirus', {})
		if isinstance(av, dict):
			av_ok = (av.get('present') and av.get('enabled'))
		else:
			av_ok = av
		slp = res.get('inactivity_sleep', {})
		if isinstance(slp, dict):
			mins = slp.get('sleep_minutes')
		else:
			mins = None
		row = [
			m.machine_id,
			m.os,
			m.last_checkin.isoformat(),
			str(disk_ok),
			str(up_ok),
			str(av_ok),
			str(mins if mins is not None else ""),
		]
		lines.append(",".join(row))
	csv_data = "\n".join(lines)
	return Response(content=csv_data, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=machines.csv"})
