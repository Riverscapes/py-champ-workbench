#! /bin/bash
python3 -m venv .venv

.venv/bin/pip --timeout=120 install -r requirements.txt