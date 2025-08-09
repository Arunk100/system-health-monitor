"""Backend configuration values."""
import os

# Optional API key to secure /report endpoint. If set, clients must send X-API-Key header.
API_KEY = os.getenv("SYSTEM_HEALTH_API_KEY") or None

# Future: place DB URL override here if needed
