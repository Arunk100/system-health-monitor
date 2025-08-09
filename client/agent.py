import time
import json
import hashlib
import platform
import requests
from checks import run_all_checks
from config import API_URL, CHECK_INTERVAL_MINUTES, API_KEY
from utils import get_machine_id, load_last_report, save_last_report

def main():
    machine_id = get_machine_id()
    last_report = load_last_report()
    while True:
        results = run_all_checks()
        report = {
            "machine_id": machine_id,
            "os": platform.system(),
            "timestamp": int(time.time()),
            "results": results,
        }
        report_hash = hashlib.sha256(json.dumps(report, sort_keys=True).encode()).hexdigest()
        if not last_report or last_report.get("hash") != report_hash:
            attempt = 0
            backoff = 2
            while attempt < 3:
                try:
                    headers = {"X-API-Key": API_KEY} if API_KEY else {}
                    resp = requests.post(f"{API_URL}/report", json=report, headers=headers, timeout=10)
                    resp.raise_for_status()
                    print("Reported system health.")
                    save_last_report({"hash": report_hash})
                    break
                except Exception as e:
                    attempt += 1
                    if attempt >= 3:
                        print(f"Failed to report after {attempt} attempts: {e}")
                    else:
                        print(f"Report attempt {attempt} failed: {e}; retrying in {backoff}s")
                        time.sleep(backoff)
                        backoff = min(backoff * 2, 60)
            last_report = load_last_report()
        else:
            print("No change in system health, not reporting.")
        time.sleep(CHECK_INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    main()
