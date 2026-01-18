# University Admission Management System

A full-stack web application designed to manage the undergraduate admission process of a university.  
The system automates **application submission**, **merit-based ranking**, **document verification**, and **seat allocation** across multiple departments using a transparent and rule-driven workflow.

---

## 📌 Project Overview

This project simulates a real-world university admission portal where:

- Students can register, apply for admission, upload documents, and track their application status.
- Admins can verify documents, allocate seats based on merit, and view department-wise merit lists.
- Admission decisions are made automatically based on predefined academic criteria.

The project emphasizes:
- **Sorting algorithms**
- **Business logic implementation**
- **Data validation**
- **Role-based access control**
- **Clean backend–frontend integration**

---

## 🎯 Key Features

### 👨‍🎓 Student Module
- Secure student registration and login
- One-time application submission
- Upload of verification documents (PDF)
- Real-time tracking of:
  - Document verification status
  - Seat allocation status

### 🧑‍💼 Admin Module
- Secure admin login
- Review and verify uploaded student documents
- Approve or reject applications
- Automated seat allocation based on merit and seat availability
- Department-wise merit list visualization

### ⚙️ Core System Logic
- Merit-based sorting using:
  - Entrance exam score
  - 12th-grade percentage
  - 10th-grade percentage
  - Age (tie-breaker)
- Fixed seat capacity per department
- Automatic seat allocation upon document approval
- Prevention of duplicate applications

---

## 🏗️ System Architecture

**Technology Stack**
- **Backend**: Python (Flask)
- **Frontend**: HTML, CSS, Bootstrap, Jinja2
- **Database**: PostgreSQL (via SQLAlchemy ORM)
- **Authentication**: Session-based
- **Email**: Flask-Mail (mock / optional)

**Architecture Style**
- Monolithic Flask application
- MVC-inspired separation:
  - Models → Database schema
  - Routes → Business logic
  - Templates → Presentation layer

---

## 🗂️ Project Structure

