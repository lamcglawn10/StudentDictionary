# Student Dictionary: persistent Flask API

The real course example is in studentdictionary/, not the older Project/ starter.
API methods and paths remain unchanged. Local SQLite and AWS EC2 PostgreSQL
use the same SQLAlchemy model.

## Windows first run

From the repo root:

~~~powershell
cd studentdictionary
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m flask --app app db upgrade
python -m flask --app app run
~~~

**Run the migration before starting the app.** The database is persisted
across application restarts. If already cloned, do not clone again.

## EC2 PostgreSQL setup

Install PostgreSQL on Ubuntu and create a dedicated database and login role.
Keep PostgreSQL port 5432 private. On EC2 inside studentdictionary/:

~~~bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
chmod 600 .env
# Edit DATABASE_URL, e.g. postgresql+psycopg://student_app:ENCODED_PASSWORD@127.0.0.1:5432/student_dictionary
.venv/bin/python -m flask --app app db upgrade
.venv/bin/python -m flask --app app run --host 127.0.0.1
~~~

Never commit .env or expose PostgreSQL publicly. Use HTTPS, Gunicorn and
Nginx for public hosting, not Flask's development server.

## Existing endpoints

GET /api/v1/students; POST /api/v1/students; GET /api/v1/students/1;
PUT /api/v1/students/1; DELETE /api/v1/students/1.

POST example JSON: {"name":"Aaron","age":25,"email":"aaron@example.com"}
PUT example JSON: {"age":26}. Database assigns the student ID.

## Verify

~~~bash
python -m pytest tests -v
python -m flask --app app db current
~~~

Tests cover API CRUD and persistence using SQLite.
AWS PostgreSQL installation, migration and live HTTP tests are pending.
The existing deploy/ scripts and GitHub Actions target Project/, not
studentdictionary/, and are not yet a verified deployment path for this app.
