"""WSGI entrypoint for running the Recipe Server application."""
from __future__ import annotations

import os

from app import create_app

config_name = os.getenv("FLASK_CONFIG")
app = create_app(config_name)
