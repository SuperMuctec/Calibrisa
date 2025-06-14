#!/bin/bash

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

mkdir databases

touch .env

python3 setup.py

python3 main.py

chmod +x run.sh