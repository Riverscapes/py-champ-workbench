#! /bin/bash
python3 -m venv .venv

.venv/Scripts/pip --timeout=120 install -r requirements.txt