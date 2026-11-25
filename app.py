"""Student Directory REST API backed by SQLite locally or PostgreSQL on EC2."""

import os

from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()


class Student(db.Model):
    """Persist one student as a database row."""

    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(254), nullable=False, default="")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "age": self.age, "email": self.email}


def create_app(database_url=None):
    """Create an independently configurable Flask application (also used by tests)."""
    app = Flask(__name__)

    uri = database_url or os.environ.get("DATABASE_URL", "sqlite:///students.db")
    if uri.startswith("postgres://"):
        uri = "postgresql+psycopg://" + uri[len("postgres://"):]
    elif uri.startswith("postgresql://"):
        uri = "postgresql+psycopg://" + uri[len("postgresql://"):]

    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate.init_app(app, db)

    @app.get("/api/v1/students")
    def get_students():
        students = db.session.execute(db.select(Student).order_by(Student.id)).scalars().all()
        return jsonify([student.to_dict() for student in students])

    @app.post("/api/v1/students")
    def create_student():
        data = request.get_json(silent=True)
        if not isinstance(data, dict) or "name" not in data or "age" not in data:
            return jsonify({"error": "Invalid input"}), 400
        if not valid_student_fields(data["name"], data["age"], data.get("email", "")):
            return jsonify({"error": "Invalid input types"}), 400

        student = Student(name=data["name"], age=data["age"], email=data.get("email", ""))
        db.session.add(student)
        db.session.commit()
        return jsonify(student.to_dict()), 201

    @app.get("/api/v1/students/<int:student_id>")
    def get_student(student_id):
        student = db.session.get(Student, student_id)
        if student is None:
            return jsonify({"error": "Student not found"}), 404
        return jsonify(student.to_dict())

    @app.put("/api/v1/students/<int:student_id>")
    def update_student(student_id):
        student = db.session.get(Student, student_id)
        if student is None:
            return jsonify({"error": "Student not found"}), 404

        data = request.get_json(silent=True)
        if not isinstance(data, dict) or not data:
            return jsonify({"error": "Invalid input"}), 400

        name = data.get("name", student.name)
        age = data.get("age", student.age)
        email = data.get("email", student.email)
        if not valid_student_fields(name, age, email):
            return jsonify({"error": "Invalid input types"}), 400

        student.name, student.age, student.email = name, age, email
        db.session.commit()
        return jsonify(student.to_dict())

    @app.delete("/api/v1/students/<int:student_id>")
    def delete_student(student_id):
        student = db.session.get(Student, student_id)
        if student is None:
            return jsonify({"error": "Student not found"}), 404
        db.session.delete(student)
        db.session.commit()
        return jsonify({"message": "Student deleted"})

    return app


def valid_student_fields(name, age, email):
    """Apply existing field types, with bounds and non-empty student names."""
    return (
        isinstance(name, str)
        and bool(name.strip())
        and len(name) <= 120
        and type(age) is int
        and 0 <= age <= 150
        and isinstance(email, str)
        and len(email) <= 254
    )


app = create_app()
