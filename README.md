# 🛡️ Secure Ticket Management System (STMS)

## 📖 Project Overview

Secure Ticket Management System (STMS) is a web-based enterprise support ticket management platform developed as an MCA Major Project.

The system enables organizations to manage support requests, assign tickets, monitor issue resolution, generate reports, and maintain secure role-based access for different stakeholders including Administrators, Managers, Engineers, and Customers.

The project simulates a real-world IT Service Desk environment and incorporates modern UI design, analytics dashboards, notification management, project-based access control, and ticket lifecycle management.

---

## 🎯 Objectives

* Provide a centralized ticket management platform.
* Enable secure role-based access control.
* Improve ticket tracking and issue resolution workflow.
* Generate analytical reports and dashboards.
* Simulate enterprise-level support management processes.
* Enhance customer and project-specific security controls.

---

# 🚀 Key Features

## 🔐 Authentication & Authorization

* Secure Login System
* Session Management
* Role-Based Access Control (RBAC)
* Admin Authentication
* Manager Authentication
* Engineer Authentication
* Customer Authentication

---

## 🎫 Ticket Management

* Create Support Tickets
* View Ticket Details
* Update Ticket Status
* Ticket Assignment Workflow
* Search Tickets
* Status-Based Filtering
* Ticket Notes & Comments
* File Attachment Upload
* Ticket Archiving

---

## 👥 User Management

* Add New Users
* Edit User Information
* Delete Users
* Role Assignment
* User Access Control

---

## 📁 Project Management

* Project Creation & Management
* User ↔ Project Mapping
* Manager ↔ Project Assignment
* Customer ↔ Project Assignment
* Customer Project Lock
* Project-Based Ticket Visibility

---

## 🔔 Notification System

* Global Notification Engine
* Ticket Creation Notifications
* Ticket Status Update Notifications
* Comment Notifications
* Unread Notification Counter
* Mark Notifications as Read
* Clear All Notifications
* Direct Ticket Navigation from Notifications

---

## 📊 Reports & Analytics

### Admin Reports

* Total Tickets
* Open Tickets
* In Progress Tickets
* Resolved Tickets

### Manager Reports

* Project-Specific Reports
* Assigned Project Analytics

### Interactive Charts

* Ticket Status Distribution
* Ticket Priority Distribution
* Project Distribution Analytics

---

## 🌙 Dark Mode

* Global Dark Mode Toggle
* Persistent User Preference
* Dashboard Dark Theme
* Form Dark Theme
* Report Page Dark Theme

---

## 🛡️ Security Features

* Session-Based Authentication
* Role-Based Route Protection
* Customer Data Isolation
* Project-Level Access Restrictions
* Secure File Upload Handling
* Environment Variable Configuration

---

# 👤 User Roles

## Administrator

* Manage Users
* Manage Projects
* Create Tickets
* Assign Tickets
* Access All Reports
* View All Tickets

## Manager

* Access Assigned Projects Only
* Create Tickets
* View Project Reports
* Monitor Project Tickets

## Engineer

* View Assigned Tickets
* Update Ticket Status
* Add Notes & Comments

## Customer

* Create Tickets
* View Own Tickets
* Receive Notifications
* Access Assigned Project Only

---

# 🛠️ Technology Stack

| Technology   | Purpose                   |
| ------------ | ------------------------- |
| Python       | Backend Development       |
| Flask        | Web Framework             |
| MySQL        | Database Management       |
| HTML5        | Structure                 |
| CSS3         | Styling                   |
| JavaScript   | Client-Side Functionality |
| Chart.js     | Analytics & Reporting     |
| Jinja2       | Template Rendering        |
| Git & GitHub | Version Control           |

---

# 🗄️ Database Design

Main Tables Used:

* users
* tickets
* projects
* user_projects
* ticket_notes
* notifications

Relationships:

* Users ↔ Projects
* Projects ↔ Tickets
* Tickets ↔ Notifications
* Tickets ↔ Notes

---

# 📂 Project Structure

```text
secure-ticket-management-system/
│
├── static/
│   ├── css/
│   │   └── dark-mode.css
│   └── js/
│       └── dark-mode.js
│
├── templates/
│   ├── index.html
│   ├── admin_dashboard.html
│   ├── manager_dashboard.html
│   ├── engineer_dashboard.html
│   ├── customer_dashboard.html
│   ├── create_ticket.html
│   ├── view_ticket.html
│   ├── reports.html
│   ├── manager_reports.html
│   ├── manage_users.html
│   ├── archived_tickets.html
│   ├── notifications.html
│   ├── settings.html
│   └── forgot_password.html
│
├── uploads/
├── app.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

# ⚙️ Installation & Setup

## Clone Repository

```bash
git clone https://github.com/Mayuresh-G-Mhatre/secure-ticket-management-system.git
```

## Navigate to Project

```bash
cd secure-ticket-management-system
```

## Create Virtual Environment

```bash
python -m venv venv
```

## Activate Environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Configure Environment Variables

Create `.env`

```env
MYSQL_PASSWORD=your_mysql_password
SECRET_KEY=your_secret_key
```

## Run Application

```bash
python app.py
```

Application URL:

```text
http://127.0.0.1:5000
```

---

# 📸 Screenshots

## Login Page

(Add Screenshot)

## Admin Dashboard

(Add Screenshot)

## Manager Dashboard

(Add Screenshot)

## Engineer Dashboard

(Add Screenshot)

## Customer Dashboard

(Add Screenshot)

## Reports & Analytics

(Add Screenshot)

## Notification System

(Add Screenshot)

---

# 🔮 Future Scope

* Email-Based Password Recovery
* SLA Management
* Email Notifications
* SMS Notifications
* REST API Integration
* Mobile Application
* Multi-Tenant Support
* AWS Cloud Deployment
* Real-Time Ticket Updates

---

# 📊 Project Status

✅ Development Completed

✅ Role-Based Access Control Implemented

✅ Notification System Implemented

✅ Reporting Dashboard Implemented

✅ Dark Mode Implemented

🟡 Deployment In Progress

🟡 Documentation In Progress

---

# 👨‍💻 Developer

**Mayuresh G. Mhatre**

Master of Computer Applications (MCA)

Major Project – Secure Ticket Management System (STMS)

2025–2026

---

# ⭐ GitHub Repository

If you found this project useful, please consider giving it a ⭐ on GitHub.
