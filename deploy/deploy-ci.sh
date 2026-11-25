#!/usr/bin/env bash
# Hour 6: deploy the CI-built Student Dictionary bundles to an existing Hour 5 EC2.
# Run as ubuntu. Backend .env/.venv and PostgreSQL data are NEVER transferred/overwritten.
set -Eeuo pipefail

APP="/home/ubuntu/studentdictionary"
WEB="/var/www/student-dictionary"
STAGE="/home/ubuntu/student-dictionary-ci-staging"
BACKUP="/home/ubuntu/student-dictionary-release-backup"
NEW_WEB="/var/www/student-dictionary.next"
ROLLBACK_WEB="/var/www/student-dictionary.previous"

failed() {
  code=$?
  trap - ERR
  echo "Deployment failed (exit $code). Restoring the previous app files and static site." >&2
  if [[ -f "$BACKUP/app.py" ]]; then
    cp "$BACKUP/app.py" "$APP/app.py"
    cp "$BACKUP/requirements.txt" "$APP/requirements.txt"
    if [[ -d "$BACKUP/migrations" ]]; then
      rm -rf "$APP/migrations"
      cp -a "$BACKUP/migrations" "$APP/migrations"
    fi
  fi
  if sudo test -d "$ROLLBACK_WEB"; then
    sudo rm -rf "$WEB"
    sudo mv "$ROLLBACK_WEB" "$WEB"
  fi
  sudo systemctl restart student-dictionary || true
  echo "App/static files restored where backups were available. DATABASE MIGRATIONS ARE NOT ROLLED BACK." >&2
  exit "$code"
}
cd "$STAGE"
test -f studentdictionary-source.tar.gz
test -f studentdictionary-dist.tar.gz
test -f "$APP/.env"
test -x "$APP/.venv/bin/python"
test -x "$APP/.venv/bin/gunicorn"
test -f "$WEB/index.html"
# This script only manages the already configured Hour 5 service/site.
sudo systemctl is-enabled student-dictionary >/dev/null
sudo nginx -t

# Prepare backups prior to modifying a running installation.
rm -rf "$BACKUP"
mkdir -p "$BACKUP"
cp "$APP/app.py" "$APP/requirements.txt" "$BACKUP/"
cp -a "$APP/migrations" "$BACKUP/migrations"
# Activate recovery only after creating a valid backup.
trap failed ERR
sudo rm -rf "$ROLLBACK_WEB" "$NEW_WEB"
sudo mkdir -p "$NEW_WEB"
sudo tar -xzf studentdictionary-dist.tar.gz -C "$NEW_WEB"
sudo test -f "$NEW_WEB/index.html"

# Release source contains ONLY reviewed tracked code. Never copy .env/.venv.
tar -xzf studentdictionary-source.tar.gz -C "$APP" app.py requirements.txt migrations deploy
chmod 600 "$APP/.env"
cd "$APP"
.venv/bin/python -m pip install -r requirements.txt
# Migration versions must be backwards-compatible: failure recovery cannot undo a DB schema change.
.venv/bin/python -m flask --app app db upgrade

# Replace the static site only after build and database migration succeed.
sudo mv "$WEB" "$ROLLBACK_WEB"
sudo mv "$NEW_WEB" "$WEB"
sudo find "$WEB" -type d -exec chmod 755 {} +
sudo find "$WEB" -type f -exec chmod 644 {} +
sudo nginx -t
sudo systemctl restart student-dictionary
sudo systemctl reload nginx

# Local smoke checks: public access is separately controlled by the EC2 security group.
curl --fail --silent --show-error --max-time 15 http://127.0.0.1:8000/api/v1/students >/dev/null
curl --fail --silent --show-error --max-time 15 http://127.0.0.1/api/v1/students >/dev/null
curl --fail --silent --show-error --max-time 15 http://127.0.0.1/ >/dev/null
sudo systemctl is-active --quiet student-dictionary
sudo systemctl is-active --quiet nginx
echo "Student Dictionary deployment smoke tests PASSED."
echo "Static site previous copy: $ROLLBACK_WEB; app source backup: $BACKUP"
