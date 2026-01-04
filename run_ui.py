#!/usr/bin/env python3
"""Run the NiceGUI app."""

from app.ui.niceui import build_ui
from nicegui import ui

# Build the UI
build_ui()

# Run the app
ui.run(host="0.0.0.0", port=8080, reload=False)
