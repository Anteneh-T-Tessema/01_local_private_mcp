#!/bin/zsh
# Script to set up Python virtual environment and install requirements
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
