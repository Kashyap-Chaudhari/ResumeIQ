#!/bin/bash
echo "BUILD START"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 manage.py collectstatic --noinput --clear
echo "BUILD END"
