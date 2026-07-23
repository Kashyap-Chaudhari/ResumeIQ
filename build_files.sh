#!/bin/bash
echo "BUILD START"
set -e
python3 -m pip install -r requirements.txt --break-system-packages
python3 manage.py collectstatic --noinput --clear
echo "BUILD END"
