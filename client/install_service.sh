#!/bin/bash
# Install as systemd/launchd/Windows service
# Linux example:
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
	sudo cp agent.py /usr/local/bin/system-health-agent.py
	sudo bash -c 'cat > /etc/systemd/system/system-health-agent.service <<EOF
[Unit]
Description=System Health Agent

[Service]
ExecStart=/usr/bin/python3 /usr/local/bin/system-health-agent.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF'
	sudo systemctl daemon-reload
	sudo systemctl enable system-health-agent
	sudo systemctl start system-health-agent
	echo "Installed as systemd service."
else
	echo "Manual install required for this OS."
fi
