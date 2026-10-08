from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import re
from urllib.parse import urlparse

import pymysql
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "studentdb"),
    "cursorclass": pymysql.cursors.DictCursor,
}


def get_connection():
    return pymysql.connect(**DB_CONFIG)


def validate_student_id(value):
    try:
        student_id = int(value)
    except (TypeError, ValueError) as error:
        raise ValueError("Invalid student ID") from error

    if student_id <= 0:
        raise ValueError("Invalid student ID")

    return student_id


def normalize_student_data(data):
    if not isinstance(data, dict):
        raise ValueError("Request body must be a JSON object")

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    course = str(data.get("course", "")).strip()

    if not name or len(name) > 100:
        raise ValueError("Name must be between 1 and 100 characters")

    if not EMAIL_PATTERN.fullmatch(email):
        raise ValueError("A valid email address is required")

    if not course or len(course) > 100:
        raise ValueError("Course must be between 1 and 100 characters")

    return {
        "name": name,
        "email": email,
        "course": course
    }


def send_json(handler, status, data):
    body = json.dumps(data).encode("utf-8")

    handler.send_response(status)

    handler.send_header(
        "Content-Type",
        "application/json; charset=utf-8"
    )

    handler.send_header(
        "Access-Control-Allow-Origin",
        os.getenv("CORS_ORIGIN", "*")
    )

    handler.send_header(
        "Access-Control-Allow-Methods",
        "GET, POST, PUT, DELETE, OPTIONS"
    )

    handler.send_header(
        "Access-Control-Allow-Headers",
        "Content-Type"
    )

    handler.send_header(
        "Content-Length",
        str(len(body))
    )

    handler.end_headers()
    handler.wfile.write(body)


class StudentAPI(BaseHTTPRequestHandler):

    # Handle CORS preflight requests
    def do_OPTIONS(self):
        self.send_response(204)

        self.send_header(
            "Access-Control-Allow-Origin",
            os.getenv("CORS_ORIGIN", "*")
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, PUT, DELETE, OPTIONS"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )

        self.end_headers()

    def read_json(self):
        length = int(self.headers.get("Content-Length", 0))

        if not length:
            raise ValueError("Request body is required")

        try:
            return json.loads(
                self.rfile.read(length).decode("utf-8")
            )

        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ValueError(
                "Request body must be valid JSON"
            ) from error

    def api_path(self):
        return urlparse(self.path).path.strip("/").split("/")


    # GET /api/students
    def do_GET(self):
        parts = self.api_path()

        if parts == ["api", "students"]:
            try:
                connection = get_connection()

                try:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            """
                            SELECT id, name, email, course
                            FROM students
                            ORDER BY id
                            """
                        )

                        rows = cursor.fetchall()

                    send_json(self, 200, rows)

                finally:
                    connection.close()

            except Exception as error:
                print("DATABASE ERROR:", error)

                send_json(
                    self,
                    500,
                    {"message": str(error)}
                )

            return

        send_json(
            self,
            404,
            {"message": "Endpoint not found"}
        )

    def do_POST(self):
        if self.api_path() != ["api", "students"]:
            send_json(
                self,
                404,
                {"message": "Endpoint not found"}
            )
            return

        try:
            data = normalize_student_data(
                self.read_json()
            )

            connection = get_connection()

            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO students
                        (name, email, course)
                        VALUES (%s, %s, %s)
                        """,
                        (
                            data["name"],
                            data["email"],
                            data["course"]
                        )
                    )

                    new_id = cursor.lastrowid

                connection.commit()

            finally:
                connection.close()

            send_json(
                self,
                201,
                {
                    "message": "Student created successfully",
                    "id": new_id
                }
            )

        except ValueError as error:
            send_json(
                self,
                400,
                {"message": str(error)}
            )

        except Exception as error:
            print("DATABASE ERROR:", error)

            send_json(
                self,
                500,
                {"message": "Unable to create student"}
            )

    def do_PUT(self):
        parts = self.api_path()

        if len(parts) != 3 or parts[:2] != ["api", "students"]:
            send_json(
                self,
                404,
                {"message": "Endpoint not found"}
            )
            return

        try:
            student_id = validate_student_id(parts[2])

            data = normalize_student_data(
                self.read_json()
            )

            connection = get_connection()

            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE students
                        SET name=%s, email=%s, course=%s
                        WHERE id=%s
                        """,
                        (
                            data["name"],
                            data["email"],
                            data["course"],
                            student_id
                        )
                    )

                    affected = cursor.rowcount

                connection.commit()

            finally:
                connection.close()

            if affected:
                send_json(
                    self,
                    200,
                    {"message": "Student updated successfully"}
                )
            else:
                send_json(
                    self,
                    404,
                    {"message": "Student not found"}
                )

        except ValueError as error:
            send_json(
                self,
                400,
                {"message": str(error)}
            )

        except Exception as error:
            print("DATABASE ERROR:", error)

            send_json(
                self,
                500,
                {"message": "Unable to update student"}
            )


    def do_DELETE(self):
        parts = self.api_path()

        if len(parts) != 3 or parts[:2] != ["api", "students"]:
            send_json(
                self,
                404,
                {"message": "Endpoint not found"}
            )
            return

        try:
            student_id = validate_student_id(parts[2])

            connection = get_connection()

            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM students WHERE id=%s",
                        (student_id,)
                    )

                    affected = cursor.rowcount

                connection.commit()

            finally:
                connection.close()

            if affected:
                send_json(
                    self,
                    200,
                    {"message": "Student deleted successfully"}
                )
            else:
                send_json(
                    self,
                    404,
                    {"message": "Student not found"}
                )

        except ValueError as error:
            send_json(
                self,
                400,
                {"message": str(error)}
            )

        except Exception as error:
            print("DATABASE ERROR:", error)

            send_json(
                self,
                500,
                {"message": "Unable to delete student"}
            )

if __name__ == "__main__":
    server = ThreadingHTTPServer(
        (HOST, PORT),
        StudentAPI
    )

    print(
        f"REST API running at http://{HOST}:{PORT}"
    )

    server.serve_forever()