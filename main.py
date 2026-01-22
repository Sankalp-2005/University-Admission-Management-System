# ================================
# main.py
# University Admission Management System
# Backend Application (Flask)
# ================================

import os
import hashlib
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    url_for,
    redirect,
    flash,
    session,
    Response
)


from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message


# -------------------------------
# Flask App Initialization
# -------------------------------
app = Flask(__name__)

# Secret key for session management and flash messages
app.secret_key = os.urandom(32)


# -------------------------------
# Database Configuration
# -------------------------------
# PostgreSQL database connection
# Uses Render DATABASE_URL if available, else local fallback
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:7893@localhost:5432/management"
)

# Disable modification tracking for performance
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)


# -------------------------------
# Email Configuration (Mock / Optional)
# -------------------------------
app.config["MAIL_SERVER"] = "smtp-relay.brevo.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USERNAME"] = os.getenv("user")
app.config["MAIL_PASSWORD"] = os.getenv("password")
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False

# Default sender address
try:
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("sender")
except:
    app.config["MAIL_DEFAULT_SENDER"] = "elc7893@gmail.com"

# Initialize Flask-Mail
mail = Mail(app)


# ===============================
# Database Models
# ===============================

class Student(db.Model):
    """
    Stores student authentication credentials.
    """
    __tablename__ = "students"

    student_id = db.Column(db.Integer, primary_key=True)
    student_username = db.Column(db.String(200))
    student_password_hash_hex = db.Column(db.String(200))


class Admin(db.Model):
    """
    Stores admin login credentials.
    """
    __tablename__ = "admins"

    admin_id = db.Column(db.Integer, primary_key=True)
    admin_username = db.Column(db.String(200))
    admin_password = db.Column(db.String(200))


class Application(db.Model):
    """
    Stores student application details and uploaded documents.
    """
    __tablename__ = "applications"

    application_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer)
    student_name = db.Column(db.String(200))
    student_gender = db.Column(db.String(200))
    student_email = db.Column(db.String(200))
    student_age = db.Column(db.Integer)
    department = db.Column(db.String(200))
    entrance_marks = db.Column(db.Integer)
    percentage_10th = db.Column(db.Integer)
    percentage_12th = db.Column(db.Integer)
    document_status = db.Column(db.String(200))
    documents = db.Column(db.LargeBinary)


class Allocation(db.Model):
    """
    Stores seat allocation results for applications.
    """
    __tablename__ = "allocations"

    allocation_id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer)
    department_id = db.Column(db.Integer)
    allocation_status = db.Column(db.String(200))


class Department(db.Model):
    """
    Stores department metadata and seat availability.
    """
    __tablename__ = "departments"

    department_id = db.Column(db.Integer, primary_key=True)
    department_name = db.Column(db.String(200))
    total_seats = db.Column(db.Integer)
    filled_seats = db.Column(db.Integer)


# ===============================
# Authentication Decorators
# ===============================

def student_signin_required(view):
    """
    Protects routes that require student authentication.
    Redirects unauthenticated users to home page.
    """
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "student_id" not in session:
            flash("Please SignIn to continue", "danger")
            return redirect(url_for("home"))
        return view(*args, **kwargs)
    return wrapped


def admin_signin_required(view):
    """
    Protects routes that require admin authentication.
    Redirects unauthenticated admins to home page.
    """
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "admin_id" not in session:
            flash("Please SignIn to continue", "danger")
            return redirect(url_for("home"))
        return view(*args, **kwargs)
    return wrapped


# ===============================
# General Routes
# ===============================

@app.route("/")
def transfer():
    """
    Redirect root URL to home page.
    """
    return redirect(url_for("home"))


@app.route("/home")
def home():
    """
    Home page.
    Initializes default departments on first run.
    """
    if not Department.query.all():
        department_cs = Department(
            department_name="CS",
            total_seats=300,
            filled_seats=0
        )
        department_mech = Department(
            department_name="Mechanical",
            total_seats=100,
            filled_seats=0
        )
        department_civil = Department(
            department_name="Civil",
            total_seats=100,
            filled_seats=0
        )
        db.session.add(department_cs)
        db.session.add(department_mech)
        db.session.add(department_civil)
        db.session.commit()

    return render_template("home.html")


# ===============================
# Student Authentication
# ===============================

@app.route("/student-signin", methods=["GET", "POST"])
def student_signin():
    """
    Handles student login.
    """
    if request.method == "POST":
        username = request.form["username"]
        hashed_hex_password = hashlib.sha256(
            request.form["password"].encode()
        ).hexdigest()

        student = Student.query.filter_by(student_username=username).first()

        if not student:
            flash("Invalid username", "danger")
            return redirect(url_for("student_signin"))

        if hashed_hex_password != student.student_password_hash_hex:
            flash("Invalid Password", "danger")
            return redirect(url_for("student_signin"))

        session["student_id"] = student.student_id
        session["student_username"] = student.student_username

        return redirect(url_for("student_dashboard"))

    return render_template("student_signin.html")


@app.route("/student-signup", methods=["GET", "POST"])
def student_signup():
    """
    Handles student registration.
    """
    if request.method == "POST":
        username = request.form["username"]
        hashed_hex_password = hashlib.sha256(
            request.form["password"].encode()
        ).hexdigest()

        if Student.query.filter_by(student_username=username).first():
            flash("User already exists", "danger")
            return redirect(url_for("student_signup"))

        student = Student(
            student_username=username,
            student_password_hash_hex=hashed_hex_password
        )

        db.session.add(student)
        db.session.commit()

        flash("Account Created, Sign In to continue", "success")
        return redirect(url_for("student_signin"))

    return render_template("student_signup.html")


# ===============================
# Admin Authentication
# ===============================

@app.route("/admin-signin", methods=["GET", "POST"])
def admin_signin():
    """
    Handles admin login.
    Inserts default admin credentials if not present.
    """
    if not Admin.query.filter_by(admin_username="admin").first():
        default_admin = Admin(
            admin_username="admin",
            admin_password="12345"
        )
        db.session.add(default_admin)
        db.session.commit()

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        admin = Admin.query.filter_by(admin_username=username).first()

        if not admin:
            flash("Invalid username", "danger")
            return redirect(url_for("admin_signin"))

        if password != admin.admin_password:
            flash("Invalid Password", "danger")
            return redirect(url_for("admin_signin"))

        session["admin_id"] = admin.admin_id
        session["admin_username"] = admin.admin_username

        return redirect(url_for("admin_dashboard"))

    return render_template("admin_signin.html")


# ===============================
# Dashboards
# ===============================

@app.route("/admin-dashboard")
@admin_signin_required
def admin_dashboard():
    """
    Admin dashboard page.
    """
    return render_template("admin_dashboard.html")


@app.route("/student-dashboard")
@student_signin_required
def student_dashboard():
    """
    Student dashboard page.
    """
    return render_template("student_dashboard.html")


# ===============================
# Application Submission
# ===============================

@app.route("/application-form", methods=["GET", "POST"])
@student_signin_required
def application_form():
    """
    Allows students to submit a single application.
    Prevents duplicate submissions.
    """
    existing_application = Application.query.filter_by(
        student_id=session["student_id"]
    ).first()

    if existing_application:
        flash("You can submit only one application.", "danger")
        return redirect(url_for("student_dashboard"))

    if request.method == "POST":
        application = Application(
            student_id=session["student_id"],
            student_name=request.form["name"],
            student_age=request.form["age"],
            student_gender=request.form["gender"],
            student_email=request.form["email"],
            department=request.form["department"],
            entrance_marks=request.form["entrance_score"],
            percentage_10th=request.form["percentage_10"],
            percentage_12th=request.form["percentage_12"],
            document_status="Pending",
            documents=request.files["documents"].read()
        )

        db.session.add(application)
        db.session.commit()

        flash("Application submitted successfully.", "success")
        return redirect(url_for("student_dashboard"))

    return render_template("application_form.html")


# ===============================
# Application Status
# ===============================

@app.route("/application-status")
@student_signin_required
def application_status():
    """
    Displays document and allocation status for a student.
    """
    application = Application.query.filter_by(
        student_id=session["student_id"]
    ).first()

    if not application:
        flash("Please fill the application form first.", "danger")
        return redirect(url_for("student_dashboard"))

    allocation_status = "Document verification is pending"

    if application.document_status == "Rejected":
        allocation_status = "Documents not verified"

    elif application.document_status == "Approved":
        allocation = Allocation.query.filter_by(
            application_id=application.application_id
        ).first()

        if allocation:
            allocation_status = allocation.allocation_status

    return render_template(
        "application_status.html",
        student_name=application.student_name,
        document_status=application.document_status,
        allocation_status=allocation_status
    )


# ===============================
# Admin Document Review
# ===============================

@app.route("/view-aadhaar/<int:student_id>")
@admin_signin_required
def view_aadhaar(student_id):
    """
    Streams uploaded PDF documents for admin verification.
    """
    application = Application.query.filter_by(student_id=student_id).first_or_404()
    return Response(
        application.documents,
        mimetype="application/pdf",
        headers={"Content-Disposition": "inline"}
    )


@app.route("/approve-documents", methods=["GET", "POST"])
@admin_signin_required
def approve_documents():

    if request.method == "POST":
        student_id = request.form["student_id"]
        status = request.form["status"]

        application = Application.query.filter_by(student_id=student_id).first()
        department = Department.query.filter_by(
            department_name=application.department
        ).first()

        application.document_status = status

        if status == "Rejected":
            try:
                msg = Message(
                    subject="Documents Rejected",
                    recipients=[application.student_email]
                )
                msg.body = "Your submitted documents have been rejected by the admissions office."
                mail.send(msg)
            except:
                pass

        elif status == "Approved":
            try:
                msg = Message(
                    subject="Documents Approved",
                    recipients=[application.student_email]
                )
                msg.body = "Your documents have been verified successfully."
                mail.send(msg)
            except:
                pass

            if department.filled_seats < department.total_seats:
                allocation = Allocation(
                    application_id=application.application_id,
                    department_id=department.department_id,
                    allocation_status="Allocated"
                )
                department.filled_seats += 1

                try:
                    msg = Message(
                        subject="Admission Offer",
                        recipients=[application.student_email]
                    )
                    msg.body = f"You have been allotted a seat in the {application.department} department."
                    mail.send(msg)
                except:
                    pass

            else:
                allocation = Allocation(
                    application_id=application.application_id,
                    department_id=department.department_id,
                    allocation_status="Not Allocated"
                )

            db.session.add(allocation)

        db.session.commit()
        return redirect(url_for("approve_documents"))

    students = Application.query.filter_by(
        document_status="Pending"
    ).order_by(
        Application.entrance_marks.desc(),
        Application.percentage_12th.desc(),
        Application.percentage_10th.desc(),
        Application.student_age.desc()
    ).all()

    return render_template(
        "approve_documents.html",
        admin_name=session["admin_username"],
        students=students
    )


# ===============================
# Merit List
# ===============================

@app.route("/merit-list")
@admin_signin_required
def merit_departments():
    """
    Displays department-wise merit list navigation.
    """
    return render_template("departments.html")


@app.route("/merit-list/<dept>")
@admin_signin_required
def department_merit(dept):
    """
    Displays allocated students for a department
    ordered by merit.
    """
    department = Department.query.filter_by(department_name=dept).first()

    students = (
        Application.query
        .join(Allocation, Allocation.application_id == Application.application_id)
        .filter(
            Application.department == dept,
            Allocation.allocation_status == "Allocated"
        )
        .order_by(
            Application.entrance_marks.desc(),
            Application.percentage_12th.desc(),
            Application.percentage_10th.desc(),
            Application.student_age.desc()
        )
        .all()
    )

    return render_template(
        "merit_list.html",
        department=department,
        students=students
    )


# ===============================
# Logout
# ===============================

@app.route("/logout")
def logout():
    """
    Clears session and logs out the user.
    """
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for("home"))


# ===============================
# Application Entry Point
# ===============================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
