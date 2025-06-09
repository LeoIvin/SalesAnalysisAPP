#!/usr/bin/env bash
# exit on error
set -o errexit

<<<<<<< HEAD
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate 
=======
pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
>>>>>>> 6eea30f94a8441445992e569ec24f7115bfefe95
