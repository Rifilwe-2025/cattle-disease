#!/usr/bin/env bash
# Render build command. Runs on every deploy, before the service starts.
#
# `set -o pipefail` matters alongside `-e`: collectstatic is piped to tail
# below, and without it a failure there would be masked by tail's exit 0.
set -euo pipefail

echo "--> Installing dependencies"
pip install --upgrade pip
pip install -r requirements.txt

echo "--> Collecting static files"
# --clear avoids serving a stale hashed file from a previous build.
python manage.py collectstatic --no-input --clear | tail -5

echo "--> Applying database migrations"
python manage.py migrate --no-input

echo "--> Build complete"
