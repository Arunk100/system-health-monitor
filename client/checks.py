import platform
import subprocess
import sys
import os

def is_wsl():
	try:
		with open('/proc/version','r') as f:
			return 'microsoft' in f.read().lower()
	except Exception:
		return False

WSL = is_wsl()

def check_disk_encryption():
	if WSL:
		return {"status": None, "skipped": True, "reason": "WSL environment"}
	os_name = platform.system()
	try:
		if os_name == "Windows":
			output = subprocess.check_output(['manage-bde', '-status', 'C:'], stderr=subprocess.DEVNULL, text=True)
			return {"status": "Percentage Encrypted: 100%" in output, "skipped": False}
		elif os_name == "Darwin":
			output = subprocess.check_output(['fdesetup', 'status'], stderr=subprocess.DEVNULL, text=True)
			return {"status": "FileVault is On" in output, "skipped": False}
		elif os_name == "Linux":
			output = subprocess.check_output(['lsblk', '-o', 'NAME,TYPE,MOUNTPOINT'], stderr=subprocess.DEVNULL, text=True)
			return {"status": "crypt" in output, "skipped": False}
	except Exception as e:
		return {"status": False, "error": str(e), "skipped": False}
	return {"status": False, "skipped": False}

def check_os_update_status():
	if WSL:
		return {"up_to_date": None, "skipped": True, "reason": "WSL environment"}
	os_name = platform.system()
	try:
		if os_name == "Windows":
			return {"up_to_date": True}
		elif os_name == "Darwin":
			output = subprocess.check_output(['softwareupdate', '-l'], stderr=subprocess.DEVNULL, text=True)
			return {"up_to_date": "No new software available." in output}
		elif os_name == "Linux":
			output = subprocess.check_output(['apt', 'list', '--upgradable'], stderr=subprocess.DEVNULL, text=True)
			return {"up_to_date": "upgradable from" not in output}
	except Exception:
		return {"up_to_date": False, "error": True}
	return {"up_to_date": False}

def check_antivirus_status():
	if WSL:
		return {"present": None, "enabled": None, "skipped": True, "reason": "WSL environment"}
	os_name = platform.system()
	try:
		if os_name == "Windows":
			output = subprocess.check_output(['powershell', '-Command', 'Get-MpComputerStatus'], stderr=subprocess.DEVNULL, text=True)
			return {"present": True, "enabled": "AMServiceEnabled" in output}
		elif os_name == "Darwin":
			output = subprocess.check_output(['ps', 'aux'], stderr=subprocess.DEVNULL, text=True)
			av_present = any(av in output for av in ["symantec", "sophos", "avast", "mcafee"])
			return {"present": av_present, "enabled": av_present}
		elif os_name == "Linux":
			output = subprocess.check_output(['ps', 'aux'], stderr=subprocess.DEVNULL, text=True)
			av_present = "clamd" in output or "clamav" in output
			return {"present": av_present, "enabled": av_present}
	except Exception as e:
		return {"present": False, "enabled": False, "error": str(e)}
	return {"present": False, "enabled": False}

def check_inactivity_sleep():
	if WSL:
		return {"sleep_minutes": None, "skipped": True, "reason": "WSL environment"}
	os_name = platform.system()
	try:
		if os_name == "Windows":
			# Placeholder implementation
			return {"sleep_minutes": 10}
		elif os_name == "Darwin":
			output = subprocess.check_output(['pmset', '-g', 'custom'], stderr=subprocess.DEVNULL, text=True)
			for line in output.splitlines():
				if " sleep" in line or line.strip().startswith('sleep '):
					parts = line.split()
					mins = int(parts[-1])
					return {"sleep_minutes": mins}
		elif os_name == "Linux":
			output = subprocess.check_output(['gsettings', 'get', 'org.gnome.settings-daemon.plugins.power', 'sleep-inactive-ac-timeout'], stderr=subprocess.DEVNULL, text=True)
			mins = int(output.strip()) // 60
			return {"sleep_minutes": mins}
	except Exception as e:
		return {"sleep_minutes": None, "error": str(e)}
	return {"sleep_minutes": None}

def run_all_checks():
	return {
		"disk_encryption": check_disk_encryption(),
		"os_update": check_os_update_status(),
		"antivirus": check_antivirus_status(),
		"inactivity_sleep": check_inactivity_sleep(),
		"_meta": {"wsl": WSL}
	}
