# 🛡️ Secure Ticket Management System (STMS)

<p align="center">
  <strong>A Secure, Cloud-Enabled IT Support Ticket Management Platform</strong>
</p>

<p align="center">
  <a href="https://secure-ticket-management-system.onrender.com/">
    <img src="https://img.shields.io/badge/Live%20Application-Visit%20STMS-success?style=for-the-badge&logo=render" alt="Live Application">
  </a>
  <img src="https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Flask-Web%20Framework-black?style=for-the-badge&logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/MySQL-Database-orange?style=for-the-badge&logo=mysql" alt="MySQL">
</p>

---

## 📌 Project Overview

The **Secure Ticket Management System (STMS)** is a web-based IT support and service management platform developed as an MCA Major Internship Project.

The application provides a centralized environment for organizations to create, assign, track, and resolve support tickets through a structured ticket lifecycle.

STMS implements **Role-Based Access Control (RBAC)** to provide different levels of access to Administrators, Managers, Engineers, and Customers. It also includes project-based access restrictions, notification management, reporting dashboards, and ticket activity tracking.

The system is designed to simulate a real-world enterprise IT Service Desk environment while emphasizing security, usability, and efficient support operations.

### 🌐 Live Application

**[https://secure-ticket-management-system.onrender.com/](https://secure-ticket-management-system.onrender.com/)**

### 🎯 Project Objectives

- Develop a centralized IT support ticket management platform.
- Implement authentication and role-based authorization.
- Establish structured ticket creation, assignment, and resolution workflows.
- Provide project-level access management.
- Improve communication through an integrated notification system.
- Generate analytical reports for monitoring ticket activity.
- Demonstrate cloud-enabled application deployment.

---

# 🚀 Key Features

## 🔐 1. Authentication & Authorization

- Login and logout functionality.
- Session-based authentication.
- Role-Based Access Control (RBAC).
- Role-specific dashboard access.
- Protected application routes.
- Access restrictions based on user roles.

## 🎫 2. Ticket Management

- Create and submit support tickets.
- View ticket details.
- Assign tickets to engineers.
- Update ticket status.
- Search and filter tickets.
- Manage ticket priorities.
- Add ticket notes and comments.
- Upload ticket attachments.
- Archive completed tickets.

## 👥 3. User Management

- Create new user accounts.
- Edit user information.
- Delete user accounts.
- Assign user roles.
- Manage user access.
- Associate users with projects.

## 📁 4. Project Management

- Create and manage projects.
- Map users to projects.
- Assign managers to projects.
- Associate customers with projects.
- Implement project-based access restrictions.
- Restrict ticket visibility according to project assignments.

## 🔔 5. Notification Management

- Centralized notification system.
- Ticket creation notifications.
- Ticket status update notifications.
- Comment-related notifications.
- Unread notification counter.
- Mark notifications as read.
- Clear all notifications.
- Navigate directly to tickets from notifications.

## 📊 6. Reports & Analytics

### Administrator Reports
- Total tickets.
- Open tickets.
- In-progress tickets.
- Resolved tickets.
- Overall ticket statistics.

### Manager Reports
- Project-specific ticket reports.
- Assigned project analytics.
- Project-level ticket monitoring.

### Interactive Analytics
- Ticket status distribution.
- Ticket priority distribution.
- Project distribution analytics.

## 🌙 7. Dark Mode

- Application-wide dark mode.
- Persistent user preference.
- Dashboard theme support.
- Form and report page theme support.

---

# 👤 User Roles & Permissions

| User Role | Responsibilities |
|---|---|
| **Administrator** | Manage users and projects, create and assign tickets, view all tickets and reports. |
| **Manager** | Access assigned projects, create tickets, monitor project tickets and view project reports. |
| **Engineer** | View assigned tickets, update ticket status, and add notes or comments. |
| **Customer** | Create support tickets, view own tickets, receive notifications, and access assigned projects. |

Each role has a dedicated dashboard and access permissions based on its responsibilities.

---

# 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web application framework |
| MySQL | Relational database management |
| HTML5 | Web page structure |
| CSS3 | Styling and responsive layouts |
| JavaScript | Client-side functionality |
| Chart.js | Data visualization and analytics |
| Jinja2 | Server-side template rendering |
| Git | Version control |
| GitHub | Source code repository |
| Render | Application hosting and deployment |
| Aiven | Managed MySQL database hosting |

---

# 🗄️ Database Design

The application uses a MySQL relational database to manage users, tickets, projects, and related activities.

### Main Database Tables

| Table | Description |
|---|---|
| `users` | Stores user account information and roles. |
| `tickets` | Stores support ticket information. |
| `projects` | Stores project details. |
| `user_projects` | Maintains user-to-project associations. |
| `ticket_notes` | Stores ticket notes and comments. |
| `notifications` | Stores application notifications. |

### Key Relationships

- Users ↔ Projects
- Projects ↔ Tickets
- Tickets ↔ Notes
- Tickets ↔ Notifications

---

# 🏗️ System Architecture

The application follows a Flask-based web architecture.

```text
             Users
               |
               v
       Web Browser Interface
               |
               v
       Flask Application
        (Backend Logic)
               |
       +-------+-------+
       |               |
       v               v
 Authentication    Ticket & Project
  and RBAC          Management
       |               |
       +-------+-------+
               |
               v
          MySQL Database
               |
               v
       Reports & Analytics
```

---

# 📸 Application Screenshots

The following screenshots showcase the application's user interface, role-specific dashboards, ticket management functionality, reporting modules, and additional features.


## 1. Login Page

<img width="1917" height="1027" alt="Screenshot 2026-10-29 112523" src="https://github.com/user-attachments/assets/6e790a42-c21e-40cb-bf11-f391500abe36" />


## 2. Administrator Dashboard

<img width="1917" height="1028" alt="Screenshot 2026-10-29 112543" src="https://github.com/user-attachments/assets/e7f17fac-0800-4666-8bb2-29bb06085961" />


## 3. Manager Dashboard

<img width="1917" height="1022" alt="image" src="https://github.com/user-attachments/assets/7efc0884-819f-4804-9a3d-23622c8fe8e2" />


## 4. Engineer Dashboard

<img width="1917" height="1027" alt="image" src="https://github.com/user-attachments/assets/c13c6663-0f75-44d2-8787-fd341bc73f6b" />


## 5. Customer Dashboard

<img width="1917" height="1012" alt="image" src="https://github.com/user-attachments/assets/53bde1b1-8c3a-40fd-8434-f2283e6f46c3" />


## 6. Ticket Management

<img width="1465" height="715" alt="image" src="https://github.com/user-attachments/assets/706ec7ff-18a5-4ad7-9d49-2cb161edda07" />


## 7. User Management

<img width="1481" height="816" alt="image" src="https://github.com/user-attachments/assets/6235fcb1-6f4b-4641-a578-568eabd8ea86" />


## 8. Reports & Analytics

<img width="1917" height="1005" alt="image" src="https://github.com/user-attachments/assets/b83fcc07-e581-4d1a-9930-f1d5c51cb1c9" />


## 9. Notification System

<img width="495" height="405" alt="image" src="https://github.com/user-attachments/assets/2d0c4f7b-00a0-404b-b6f9-00f7f6edf01f" />


## 10. Dark Mode

<img width="1917" height="1002" alt="image" src="https://github.com/user-attachments/assets/5cfe7aa0-7a37-4f12-951b-c3e044d47b62" />


---

# ⚙️ Installation & Local Setup

Follow these steps to run STMS on your local machine.

### Prerequisites

- Python 3.x
- MySQL database
- Git
- Code editor (VS Code recommended)

### 1. Clone the Repository

```bash
git clone https://github.com/Mayuresh-G-Mhatre/secure-ticket-management-system.git
```

### 2. Navigate to the Project Directory

```bash
cd secure-ticket-management-system
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

**Windows:**

```bash
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure Environment Variables

Create a `.env` file in the project root directory.

Add your database connection details and application secret:

```env
SECRET_KEY=your_secure_secret_key

MYSQL_HOST=your_mysql_host
MYSQL_USER=your_mysql_username
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=your_database_name
```

Replace the example values with your actual configuration.

**Important:** Never commit your `.env` file, database credentials, or secret keys to GitHub.

### 7. Configure the Database

Create the required MySQL database and tables using the project's database schema.

Ensure the database connection settings in `.env` match your MySQL configuration.

### 8. Run the Application

```bash
python app.py
```

Open the application in your browser:

```text
http://127.0.0.1:5000/
```

---

# ☁️ Deployment

STMS is deployed as a cloud-hosted web application.

| Component | Platform |
|---|---|
| Application Hosting | Render |
| Database Hosting | Aiven MySQL |
| Source Code Management | GitHub |
| Deployment Method | GitHub-connected automatic deployment |

### Live Application

**[Open Secure Ticket Management System](https://secure-ticket-management-system.onrender.com/)**

---

# 🛡️ Security Considerations

Security is an important part of the STMS implementation.

The application includes:

- Session-based authentication.
- Role-based route protection.
- Role-specific dashboard access.
- Project-based access restrictions.
- Customer-specific ticket visibility.
- Secure file upload handling.
- Environment variable-based configuration.
- Protected application routes.

**Note:** Authentication and authorization controls should be evaluated alongside object-level ticket permissions, uploaded-file access, and password storage practices.

---

# 🧪 Testing

The project includes a Python-based security testing script:

```text
test_security.py
```

The script is intended to validate authentication and role-based route access.

Run it using:

```bash
python test_security.py
```

Configure the required test credentials and application URL according to the script before execution.

---

# 🔮 Future Enhancements

The following features can be considered for future development:

- Email-based password recovery.
- Service Level Agreement (SLA) management.
- Automated email notifications.
- SMS notifications.
- REST API integration.
- Mobile application support.
- Multi-tenant architecture.
- Real-time ticket updates.
- Advanced reporting and analytics.

---

# 📊 Project Status

| Module | Status |
|---|---|
| Authentication & Authorization | ✅ Implemented |
| Role-Based Access Control | ✅ Implemented |
| Ticket Management | ✅ Implemented |
| User Management | ✅ Implemented |
| Project Management | ✅ Implemented |
| Notification System | ✅ Implemented |
| Reports & Analytics | ✅ Implemented |
| Dark Mode | ✅ Implemented |
| Cloud Deployment | ✅ Deployed |
| Documentation | 🟡 In Progress |

---

# 👨‍💻 Developer

**Mayuresh G. Mhatre**

Master of Computer Applications (MCA)  
Bharati Vidyapeeth (Deemed to be University)  
Centre for Distance and Online Education

**Project:** MCA Major Internship Project  
**Academic Year:** 2025–2026

---

# 🔗 Project Links

- **Live Application:** https://secure-ticket-management-system.onrender.com/
- **GitHub Repository:** https://github.com/Mayuresh-G-Mhatre/secure-ticket-management-system

---

<p align="center">
  <strong>⭐ If you find this project interesting, consider giving the repository a star!</strong>
</p>

<p align="center">
  Developed with ❤️ by Mayuresh G. Mhatre
</p>
