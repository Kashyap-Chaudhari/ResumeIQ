#!/bin/bash
echo "BUILD START"
set -e

python3 -m venv venv
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt
venv/bin/python manage.py collectstatic --noinput --clear

echo "BUILD END"