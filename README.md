# Student Management Portal

A responsive student records dashboard built with Next.js, Python's built-in HTTP server, PyMySQL, and MySQL.

## Architecture

Next.js frontend → Python REST API → PyMySQL → MySQL

## Prerequisites

- Node.js 18 or newer
- Python 3.9 or newer
- MySQL 8 or MariaDB

## Database setup

Run the SQL file from the project root:

```bash
mysql -u root -p < database/studentdb.sql
```

The script creates the `studentdb` database and seeds three sample students.

## Backend setup

```bash
cd backend
python -m venv .venv
.
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Set the database connection variables before starting the API:

```powershell
$env:DB_HOST = "localhost"
$env:DB_USER = "root"
$env:DB_PASSWORD = "your-password"
$env:DB_NAME = "studentdb"
python server.py
```

The API runs at `http://localhost:8000`.

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:3000`. It uses `http://localhost:8000/api/students` by default. Set `NEXT_PUBLIC_API_URL` in the frontend environment to use another backend URL.

## REST API

- `GET /api/students` — list all students
- `GET /api/students/:id` — retrieve one student
- `POST /api/students` — create a student
- `PUT /api/students/:id` — update a student
- `DELETE /api/students/:id` — delete a student

All create and update requests require a valid name, email address, and course. The API returns safe, user-facing error messages without exposing database internals.

## Production checks

```bash
cd frontend
npm run build
```

```bash
cd backend
python -m unittest -v test_server.py
```
