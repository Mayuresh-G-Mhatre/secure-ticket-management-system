import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from flask import send_from_directory
from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL

app = Flask(__name__)
load_dotenv()
UPLOAD_FOLDER = 'uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# -------------------------
# SECRET KEY
# -------------------------

app.secret_key = os.getenv('SECRET_KEY')

# -------------------------
# MYSQL CONFIGURATION
# -------------------------

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT', 3306))

mysql = MySQL(app)

# -------------------------
# NOTIFICATION FUNCTIONS
# -------------------------

def create_notification(user_id, title, message, notif_type, ticket_id=None):

    cur = mysql.connection.cursor()

    query = """
        INSERT INTO notifications
        (user_id, title, message, type, ticket_id)

        VALUES (%s, %s, %s, %s, %s)
    """

    values = (
        user_id,
        title,
        message,
        notif_type,
        ticket_id
    )

    cur.execute(query, values)

    mysql.connection.commit()

    cur.close()

# -------------------------
# NOTIFY ADMINS
# -------------------------

def notify_admins(title, message, notif_type, ticket_id):

    cur = mysql.connection.cursor()

    cur.execute("""

        SELECT id

        FROM users

        WHERE role = 'admin'

    """)

    admins = cur.fetchall()

    for admin in admins:

    #------------------------
    # SKIP SELF NOTIFICATION
    #-------------------------
        if admin[0] == session.get('user_id'):
            continue

        create_notification(

            admin[0],
            title,
            message,
            notif_type,
            ticket_id

        )

    cur.close()

# -------------------------
# NOTIFY PROJECT MANAGERS
# -------------------------

def notify_project_managers(project_id, title, message, notif_type, ticket_id):

    cur = mysql.connection.cursor()

    query = """

        SELECT users.id

        FROM users

        JOIN user_projects
        ON users.id = user_projects.user_id

        WHERE users.role = 'manager'
        AND user_projects.project_id = %s

    """

    cur.execute(query, (project_id,))

    managers = cur.fetchall()

    for manager in managers:

    #------------------------
    # SKIP SELF NOTIFICATION
    #-------------------------
        if manager[0] == session.get('user_id'):
            continue

        create_notification(

            manager[0],
            title,
            message,
            notif_type,
            ticket_id

        )

    cur.close()


# -------------------------
# NOTIFY ENGINEER
# -------------------------

def notify_engineer(engineer_id, title, message, notif_type, ticket_id):
    
    #-------------------------
    # SKIP SELF NOTIFICATION
    #-------------------------

    if engineer_id == session.get('user_id'):
        return

    create_notification(

        engineer_id,
        title,
        message,
        notif_type,
        ticket_id

    )


# -------------------------
# NOTIFY CUSTOMER
# -------------------------

def notify_customer(customer_id, title, message, notif_type, ticket_id):
    #-------------------------
    # SKIP SELF NOTIFICATION
    #-------------------------
    
    if customer_id == session.get('user_id'):
        return

    create_notification(

        customer_id,
        title,
        message,
        notif_type,
        ticket_id

    )

def get_notifications():

    if not session.get('user_id'):
        return []

    cur = mysql.connection.cursor()

    query = """

        SELECT
            id,
            title,
            message,
            is_read,
            ticket_id,
            created_at

        FROM notifications

        WHERE user_id = %s

        ORDER BY created_at DESC

        LIMIT 10

    """

    cur.execute(query, (session.get('user_id'),))

    notifications = cur.fetchall()

    cur.close()

    return notifications


@app.context_processor

def inject_notifications():

    if 'user_id' not in session:

        return dict(
            notifications=[],
            unread_count=0
        )

    cur = mysql.connection.cursor()

    cur.execute("""

        SELECT
            id,
            title,
            message,
            is_read,
            ticket_id,
            created_at

        FROM notifications

        WHERE user_id = %s

        ORDER BY created_at DESC

        LIMIT 10

    """, (session['user_id'],))

    notifications = cur.fetchall()

    # UNREAD COUNT

    cur.execute("""

        SELECT COUNT(*)

        FROM notifications

        WHERE user_id = %s
        AND is_read = 0

    """, (session['user_id'],))

    unread_count = cur.fetchone()[0]

    cur.close()

    return dict(
        notifications=notifications,
        unread_count=unread_count
    )
@app.route('/notification/<int:notif_id>/<int:ticket_id>')
def open_notification(notif_id, ticket_id):

    if 'user_id' not in session:
        return redirect('/')

    cur = mysql.connection.cursor()

    # MARK AS READ

    cur.execute("""

        UPDATE notifications

        SET is_read = 1

        WHERE id = %s
        AND user_id = %s

    """, (

        notif_id,
        session['user_id']

    ))

    mysql.connection.commit()

    cur.close()

    return redirect(f'/ticket/{ticket_id}')

@app.route('/clear-notifications')
def clear_notifications():

    if 'user_id' not in session:
        return redirect('/')

    cur = mysql.connection.cursor()

    cur.execute("""

        DELETE FROM notifications

        WHERE user_id = %s

    """, (session['user_id'],))

    mysql.connection.commit()

    cur.close()

    return redirect(request.referrer or '/')

# -------------------------
# HOME PAGE
# -------------------------

@app.route('/')
def home():
    return render_template('index.html')

# -------------------------
# LOGIN AUTHENTICATION
# -------------------------

@app.route('/login', methods=['POST'])
def login():

    username = request.form['username']
    password = request.form['password']
    role = request.form['role']

    cur = mysql.connection.cursor()

    query = """
        SELECT * FROM users
        WHERE username=%s AND password=%s AND role=%s
    """

    cur.execute(query, (username, password, role))

    user = cur.fetchone()

    cur.close()

    if user:

        session['loggedin'] = True
        session['username'] = user[2]
        session['role'] = user[5]
        session['full_name'] = user[1]
        session['user_id'] = user[0]

        # ROLE-BASED REDIRECTION

        if role == 'admin':
            return redirect('/admin-dashboard')

        elif role == 'engineer':
            return redirect('/engineer-dashboard')

        elif role == 'manager':
            return redirect('/manager-dashboard')

        elif role == 'customer':
            return redirect('/customer-dashboard')

    else:
        return "Invalid Username, Password or Role"

# -------------------------
# DASHBOARDS
# -------------------------

@app.route('/admin-dashboard')
def admin_dashboard():

    search = request.args.get('search')
    status_filter = request.args.get('status')

    cur = mysql.connection.cursor()

    # -------------------------
    # FETCH / SEARCH / FILTER
    # -------------------------

    query = """
        SELECT
            tickets.ticket_id,
            tickets.ticket_number,
            tickets.title,
            tickets.priority,
            tickets.status,
            users.full_name

        FROM tickets

        LEFT JOIN users
        ON tickets.assigned_to = users.id

        WHERE tickets.is_archived = 0
    """

    params = []

    # SEARCH

    if search:

        query += """
            AND (
    tickets.ticket_number LIKE %s
    OR tickets.title LIKE %s
    OR users.full_name LIKE %s
)
        """

        search_term = f"%{search}%"

        params.extend([search_term, search_term,search_term])

    # STATUS FILTER

    if status_filter:

        query += """
            AND tickets.status = %s
        """

        params.append(status_filter)

    query += """
        ORDER BY tickets.created_at DESC
    """

    cur.execute(query, tuple(params))

    tickets = cur.fetchall()

    # -------------------------
    # SUMMARY COUNTS
    # -------------------------

    cur.execute("SELECT COUNT(*) FROM tickets")
    total_tickets = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM tickets
        WHERE status='Open'
    """)
    open_tickets = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM tickets
        WHERE status='In Progress'
    """)
    in_progress_tickets = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM tickets
        WHERE status='Resolved'
    """)
    resolved_tickets = cur.fetchone()[0]

    cur.close()

    return render_template(
    'admin_dashboard.html',
    tickets=tickets,
    status_filter=status_filter,
    total_tickets=total_tickets,
    open_tickets=open_tickets,
    in_progress_tickets=in_progress_tickets,
    resolved_tickets=resolved_tickets,
    search=search,
    active_page='all_tickets'
)

@app.route('/unassigned-tickets')
def unassigned_tickets():

    cur = mysql.connection.cursor()
    priority_filter = request.args.get('priority')
    search = request.args.get('search')

    query = """
        SELECT
            ticket_id,
            ticket_number,
            title,
            priority,
            status

        FROM tickets

        WHERE assigned_to IS NULL
        AND is_archived = 0
    """

    params = []

    # PRIORITY FILTER

    if priority_filter:

        query += """
            AND priority=%s
        """

        params.append(priority_filter)

    # SEARCH

    if search:

        query += """
            AND (
                ticket_number LIKE %s
                OR title LIKE %s
            )
        """

        search_term = f"%{search}%"

        params.extend([
            search_term,
            search_term
        ])

    query += """
        ORDER BY created_at DESC
    """

    cur.execute(query, tuple(params))

    tickets = cur.fetchall()
    cur.close()

    return render_template(
        'unassigned_tickets.html',
        tickets=tickets,
        search=search,
        priority_filter=priority_filter,
        active_page='unassigned_tickets'
    )
@app.route('/create-ticket', methods=['GET', 'POST'])
def create_ticket():

    cur = mysql.connection.cursor()

    # -------------------------
    # FETCH PROJECTS
    # -------------------------

    if session.get('role') in ['manager', 'customer']:

        cur.execute("""

            SELECT
                projects.id,
                projects.project_name

            FROM user_projects

            JOIN projects
            ON user_projects.project_id = projects.id

            WHERE user_projects.user_id = %s

            ORDER BY projects.project_name ASC

        """, (session.get('user_id'),))

        projects = cur.fetchall()

    else:

        cur.execute("""

            SELECT
                id,
                project_name

            FROM projects

            ORDER BY project_name ASC

        """)

        projects = cur.fetchall()

    # -------------------------
    # NEXT TICKET NUMBER
    # -------------------------

    cur.execute("SELECT COUNT(*) FROM tickets")

    count = cur.fetchone()[0] + 1

    next_ticket_number = f"ST{1000 + count}"

    # -------------------------
    # CREATE TICKET
    # -------------------------

    if request.method == 'POST':

        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        priority = request.form['priority']

        # -------------------------
        # PROJECT HANDLING
        # -------------------------

        if session.get('role') == 'customer':

            customer_id = session.get('user_id')

            cur.execute("""

                SELECT project_id

                FROM user_projects

                WHERE user_id = %s

            """, (customer_id,))

            result = cur.fetchone()

            project_id = result[0] if result else None

        else:

            project_id = request.form['project_id']

        # -------------------------
        # FILE UPLOAD
        # -------------------------

        attachment = request.files.get('attachment')

        filename = None

        if attachment and attachment.filename != '':

            filename = secure_filename(
                attachment.filename
            )

            attachment.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    filename
                )
            )

        ticket_number = next_ticket_number

        # -------------------------
        # INSERT TICKET
        # -------------------------

        query = """

            INSERT INTO tickets
            (
                ticket_number,
                title,
                description,
                category,
                priority,
                status,
                created_by,
                assigned_to,
                attachment,
                project_id
            )

            VALUES
            (
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s
            )

        """

        values = (

            ticket_number,
            title,
            description,
            category,
            priority,
            'Open',

            session.get('user_id'),

            None,

            filename,

            project_id

        )

        cur.execute(query, values)

        mysql.connection.commit()

        ticket_id = cur.lastrowid

        # -------------------------
        # NOTIFICATIONS
        # -------------------------

        notify_admins(

            "New Ticket Created",

            f"New support ticket {ticket_number} was created.",

            "ticket_created",

            ticket_id

        )

        notify_project_managers(

            project_id,

            "New Ticket Created",

            f"New support ticket {ticket_number} was created.",

            "ticket_created",

            ticket_id

        )

        cur.close()

        if session.get('role') == 'manager':
            return redirect('/manager-dashboard')

        elif session.get('role') == 'customer':
            return redirect('/customer-dashboard')

        return redirect('/admin-dashboard')

    # -------------------------
    # DEBUG
    # -------------------------

    print("ROLE =", session.get('role'))
    print("USER =", session.get('user_id'))
    print("PROJECTS =", projects)
    print("SESSION =", dict(session))

    cur.close()

    return render_template(

        'create_ticket.html',

        next_ticket_number=next_ticket_number,

        full_name=session.get('full_name'),

        projects=projects

    )

@app.route('/ticket/<int:ticket_id>')
def view_ticket(ticket_id):

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT * FROM ticket_notes
        WHERE ticket_id=%s
        ORDER BY created_at DESC
    """, (ticket_id,))

    notes = cur.fetchall()

    # -------------------------
    # FETCH TICKET
    # -------------------------

    query = """
        SELECT t.*,
               u.full_name
        FROM tickets t
        LEFT JOIN users u
        ON t.assigned_to = u.id
        WHERE t.ticket_id = %s
    """

    cur.execute(query, (ticket_id,))

    ticket = cur.fetchone()

    # -------------------------
    # FETCH ENGINEERS
    # -------------------------

    cur.execute("""
        SELECT id, full_name
        FROM users
        WHERE role='engineer'
    """)

    engineers = cur.fetchall()

    cur.close()
    

    return render_template(
    'view_ticket.html',
    ticket=ticket,
    engineers=engineers,
    notes=notes
)



@app.route('/update-status/<int:ticket_id>', methods=['POST'])
def update_status(ticket_id):

    new_status = request.form['status']

    cur = mysql.connection.cursor()

    query = """
        UPDATE tickets
        SET status = %s
        WHERE ticket_id = %s
    """

    cur.execute(query, (new_status, ticket_id))

    mysql.connection.commit()

    # -------------------------
    # STATUS NOTIFICATION
    # -------------------------

    # -------------------------
    # GET TICKET DETAILS
    # -------------------------

    cur.execute("""

        SELECT
            project_id,
            created_by,
            assigned_to

        FROM tickets

        WHERE ticket_id = %s

    """, (ticket_id,))

    ticket_data = cur.fetchone()

    project_id = ticket_data[0]
    customer_id = ticket_data[1]
    engineer_id = ticket_data[2]
    # -------------------------
    # ADMIN NOTIFICATIONS
    # -------------------------

    notify_admins(

        "Ticket Status Updated",

        f"Ticket status changed to {new_status}.",

        "status_update",

        ticket_id

    )

    # -------------------------
    # MANAGER NOTIFICATIONS
    # -------------------------

    notify_project_managers(

        project_id,

        "Ticket Status Updated",

        f"Ticket status changed to {new_status}.",

        "status_update",

        ticket_id

    )

    # -------------------------
    # CUSTOMER NOTIFICATION
    # -------------------------

    notify_customer(

        customer_id,

        "Ticket Status Updated",

        f"Your ticket status has been updated to {new_status}.",

        "status_update",

        ticket_id

    )
    # -------------------------
    # ENGINEER NOTIFICATION
    # -------------------------

    notify_engineer(

    engineer_id,

    "Ticket Status Updated",

    f"Assigned ticket status updated to {new_status}.",

    "status_update",

    ticket_id

)

    cur.close()

    return redirect(f'/ticket/{ticket_id}')

@app.route('/assign-ticket/<int:ticket_id>', methods=['POST'])
def assign_ticket(ticket_id):

    engineer_id = request.form['engineer_id']

    cur = mysql.connection.cursor()

    query = """
        UPDATE tickets
        SET assigned_to = %s
        WHERE ticket_id = %s
    """

    cur.execute(query, (engineer_id, ticket_id))

    mysql.connection.commit()

    # -------------------------
    # ASSIGNMENT NOTIFICATION
    # -------------------------

    notify_engineer(

    engineer_id,

    "New Ticket Assigned",

    f"You have been assigned a new support ticket.",

    "ticket_assigned",

    ticket_id

)
    cur.close()

    return redirect(f'/ticket/{ticket_id}')

@app.route('/archive-ticket/<int:ticket_id>', methods=['POST'])
def archive_ticket(ticket_id):

    cur = mysql.connection.cursor()

    query = """
        UPDATE tickets
        SET is_archived = 1
        WHERE ticket_id = %s
    """

    cur.execute(query, (ticket_id,))

    mysql.connection.commit()

    cur.close()

    return redirect('/admin-dashboard')

@app.route('/archived-tickets')
def archived_tickets():

    cur = mysql.connection.cursor()
    status_filter = request.args.get('status')
    search = request.args.get('search')

    query = """

    SELECT
        tickets.ticket_id,
        tickets.ticket_number,
        tickets.title,
        tickets.priority,
        tickets.status,
        users.full_name

    FROM tickets

    LEFT JOIN users
    ON tickets.assigned_to = users.id

    WHERE tickets.is_archived = 1

"""

    params = []

    # STATUS FILTER

    if status_filter:

        query += """
            AND tickets.status=%s
        """

        params.append(status_filter)

    # SEARCH

    if search:

        query += """
            AND (
                tickets.ticket_number LIKE %s
                OR tickets.title LIKE %s
                OR users.full_name LIKE %s
            )
        """

        search_term = f"%{search}%"

        params.extend([
            search_term,
            search_term,
            search_term
        ])

    query += """
        ORDER BY tickets.created_at DESC
    """

    cur.execute(query, tuple(params))

    tickets = cur.fetchall()

    cur.close()

    return render_template(
        'archived_tickets.html',
        tickets=tickets,
        search=search,
        status_filter=status_filter,
        active_page='archived_tickets'
    )

@app.route('/reports')
def reports():

    cur = mysql.connection.cursor()

    engineer_id = request.args.get('engineer_id')

    # -------------------------
    # TOTAL TICKETS
    # -------------------------

    if engineer_id:

        cur.execute("""
            SELECT COUNT(*)
            FROM tickets
            WHERE assigned_to=%s
        """, (engineer_id,))

    else:

        cur.execute("""
            SELECT COUNT(*)
            FROM tickets
        """)

    total_tickets = cur.fetchone()[0]

    # -------------------------
    # OPEN
    # -------------------------

    if engineer_id:

        cur.execute("""
            SELECT COUNT(*)
            FROM tickets
            WHERE assigned_to=%s
            AND status='Open'
        """, (engineer_id,))

    else:

        cur.execute("""
            SELECT COUNT(*)
            FROM tickets
            WHERE status='Open'
        """)

    open_tickets = cur.fetchone()[0]

    # -------------------------
    # IN PROGRESS
    # -------------------------

    if engineer_id:

        cur.execute("""
            SELECT COUNT(*)
            FROM tickets
            WHERE assigned_to=%s
            AND status='In Progress'
        """, (engineer_id,))

    else:

        cur.execute("""
            SELECT COUNT(*)
            FROM tickets
            WHERE status='In Progress'
        """)

    in_progress_tickets = cur.fetchone()[0]

    # -------------------------
    # RESOLVED
    # -------------------------

    if engineer_id:

        cur.execute("""
            SELECT COUNT(*)
            FROM tickets
            WHERE assigned_to=%s
            AND status='Resolved'
        """, (engineer_id,))

    else:

        cur.execute("""
            SELECT COUNT(*)
            FROM tickets
            WHERE status='Resolved'
        """)

    resolved_tickets = cur.fetchone()[0]

    # -------------------------
    # CLOSED
    # -------------------------

    if engineer_id:

        cur.execute("""
            SELECT COUNT(*)
            FROM tickets
            WHERE assigned_to=%s
            AND status='Closed'
        """, (engineer_id,))

    else:

        cur.execute("""
            SELECT COUNT(*)
            FROM tickets
            WHERE status='Closed'
        """)

    closed_tickets = cur.fetchone()[0]

    # -------------------------
    # CRITICAL
    # -------------------------

    if engineer_id:

        cur.execute("""
            SELECT COUNT(*)
            FROM tickets
            WHERE assigned_to=%s
            AND priority='Critical'
        """, (engineer_id,))

    else:

        cur.execute("""
            SELECT COUNT(*)
            FROM tickets
            WHERE priority='Critical'
        """)

    critical_tickets = cur.fetchone()[0]

    # -------------------------
    # ENGINEER PERFORMANCE
    # -------------------------

    cur.execute("""
        SELECT
            users.full_name,
            COUNT(tickets.ticket_id)

        FROM users

        LEFT JOIN tickets
        ON users.id = tickets.assigned_to

        WHERE users.role='engineer'

        GROUP BY users.full_name
    """)

    engineer_stats = cur.fetchall()

    # -------------------------
    # FETCH ENGINEERS
    # -------------------------

    cur.execute("""
        SELECT id, full_name
        FROM users
        WHERE role='engineer'
    """)

    engineers = cur.fetchall()

    cur.close()

    return render_template(
        'reports.html',

        total_tickets=total_tickets,
        open_tickets=open_tickets,
        in_progress_tickets=in_progress_tickets,
        resolved_tickets=resolved_tickets,
        closed_tickets=closed_tickets,
        critical_tickets=critical_tickets,

        engineer_stats=engineer_stats,

        engineers=engineers,
        selected_engineer=engineer_id,

        active_page='reports'
    )

@app.route('/settings')
def settings():

    cur = mysql.connection.cursor()

    # -------------------------
    # TOTAL USERS
    # -------------------------

    cur.execute("""
        SELECT COUNT(*)
        FROM users
    """)

    total_users = cur.fetchone()[0]

    # -------------------------
    # TOTAL ENGINEERS
    # -------------------------

    cur.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE role='engineer'
    """)

    total_engineers = cur.fetchone()[0]

    # -------------------------
    # TOTAL TICKETS
    # -------------------------

    cur.execute("""
        SELECT COUNT(*)
        FROM tickets
    """)

    total_tickets = cur.fetchone()[0]

    # -------------------------
    # ARCHIVED TICKETS
    # -------------------------

    cur.execute("""
        SELECT COUNT(*)
        FROM tickets
        WHERE is_archived = 1
    """)

    archived_tickets = cur.fetchone()[0]

    cur.close()

    return render_template(
        'settings.html',

        total_users=total_users,
        total_engineers=total_engineers,
        total_tickets=total_tickets,
        archived_tickets=archived_tickets,

        active_page='settings'
    )

@app.route('/restore-ticket/<int:ticket_id>', methods=['POST'])
def restore_ticket(ticket_id):

    cur = mysql.connection.cursor()

    query = """
        UPDATE tickets
        SET is_archived = 0
        WHERE ticket_id = %s
    """

    cur.execute(query, (ticket_id,))

    mysql.connection.commit()

    cur.close()

    return redirect('/archived-tickets')

@app.route('/manage-users')
def manage_users():

    cur = mysql.connection.cursor()
    role_filter = request.args.get('role')

    query = """
        SELECT
        id,
        full_name,
        username,
        email,
        role

    FROM users
"""

    params = []

    # ROLE FILTER

    if role_filter:

        query += """
            WHERE role=%s
        """

        params.append(role_filter)

    query += """
        ORDER BY id DESC
    """

    cur.execute(query, tuple(params))

    users = cur.fetchall()
    cur.close()

    return render_template(
        'manage_users.html',
        users=users,
        role_filter=role_filter,
        active_page='manage_users'
    )

@app.route('/add-user', methods=['GET', 'POST'])
def add_user():

    if request.method == 'POST':

        full_name = request.form['full_name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        cur = mysql.connection.cursor()

        query = """
            INSERT INTO users
            (full_name, username, email, password, role)

            VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            full_name,
            username,
            email,
            password,
            role
        )

        cur.execute(query, values)

        mysql.connection.commit()

        cur.close()

        return redirect('/manage-users')

    return render_template('add_user.html')

@app.route('/delete-user/<int:user_id>', methods=['POST'])
def delete_user(user_id):

    # Prevent deleting main admin

    if user_id == 1:

        return redirect('/manage-users')

    cur = mysql.connection.cursor()

    query = """
        DELETE FROM users
        WHERE id = %s
    """

    cur.execute(query, (user_id,))

    mysql.connection.commit()

    cur.close()

    return redirect('/manage-users')

@app.route('/add-note/<int:ticket_id>', methods=['POST'])
def add_note(ticket_id):

    if 'user_id' not in session:
        return redirect('/')

    note = request.form['note']

    if note.strip() == '':
        return redirect(f'/ticket/{ticket_id}')

    cursor = mysql.connection.cursor()

    cursor.execute("""
        INSERT INTO ticket_notes (ticket_id, user_name, note)
        VALUES (%s, %s, %s)
    """, (
        ticket_id,
        session['full_name'],
        note
    ))

    mysql.connection.commit()

    # -------------------------
    # FETCH TICKET DETAILS
    # -------------------------

    cursor.execute("""

    SELECT
        project_id,
        created_by

    FROM tickets

    WHERE ticket_id = %s

""", (ticket_id,))

    ticket_data = cursor.fetchone()

    project_id = ticket_data[0]
    customer_id = ticket_data[1]

    # -------------------------
    # ADMIN NOTIFICATIONS
    # -------------------------

    notify_admins(
        "New Comment Added",
        f"A new comment was added to the ticket.",
        "note_added",
        ticket_id
    )

    # -------------------------
    # MANAGER NOTIFICATIONS
    # -------------------------

    notify_project_managers(
        project_id,
        "New Comment Added",
        f"A new comment was added to the ticket.",
        "note_added",
        ticket_id
    )

    # -------------------------
    # CUSTOMER NOTIFICATION
    # -------------------------

    notify_customer(
        customer_id,
        "New Comment Added",
        f"A new update was added to your ticket.",
        "note_added",
        ticket_id
    )

    return redirect(f'/ticket/{ticket_id}')

@app.route('/engineer-dashboard')
def engineer_dashboard():

    engineer_id = session.get('user_id')

    cur = mysql.connection.cursor()
    status_filter = request.args.get('status')
    search = request.args.get('search')

    # -------------------------
    # FETCH ASSIGNED TICKETS
    # -------------------------

    query = """
    SELECT
        ticket_id,
        ticket_number,
        title,
        priority,
        status

    FROM tickets

    WHERE assigned_to=%s
    AND is_archived=0
    """

    params = [session['user_id']]

    # STATUS FILTER

    if status_filter:

        query += """
            AND status=%s
        """

        params.append(status_filter)

    # SEARCH

    if search:

        query += """
            AND (
                ticket_number LIKE %s
                OR title LIKE %s
            )
        """

        search_term = f"%{search}%"

        params.extend([
            search_term,
            search_term
        ])

    query += """
        ORDER BY created_at DESC
    """

    cur.execute(query, tuple(params))

    tickets = cur.fetchall()

    # -------------------------
    # TOTAL ASSIGNED
    # -------------------------

    cur.execute("""
        SELECT COUNT(*)
        FROM tickets
        WHERE assigned_to = %s
        AND is_archived = 0
    """, (engineer_id,))

    total_assigned = cur.fetchone()[0]

    # -------------------------
    # RESOLVED
    # -------------------------

    cur.execute("""
        SELECT COUNT(*)
        FROM tickets
        WHERE assigned_to = %s
        AND status='Resolved'
    """, (engineer_id,))

    resolved_tickets = cur.fetchone()[0]

    # -------------------------
    # IN PROGRESS
    # -------------------------

    cur.execute("""
        SELECT COUNT(*)
        FROM tickets
        WHERE assigned_to = %s
        AND status='In Progress'
    """, (engineer_id,))

    in_progress_tickets = cur.fetchone()[0]

    cur.close()

    return render_template(
        'engineer_dashboard.html',

        tickets=tickets,
        search=search,
        status_filter=status_filter,
        total_assigned=total_assigned,
        resolved_tickets=resolved_tickets,
        in_progress_tickets=in_progress_tickets
    )

@app.route('/manager-dashboard')
def manager_dashboard():

    # -------------------------
    # MANAGER SESSION CHECK
    # -------------------------

    if session.get('role') != 'manager':

        return redirect('/')

    cur = mysql.connection.cursor()

    manager_id = session.get('user_id')
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    # -------------------------
    # FETCH MANAGER PROJECTS
    # -------------------------

    cur.execute("""

        SELECT projects.id,
               projects.project_name

        FROM user_projects

        JOIN projects
        ON user_projects.project_id = projects.id

        WHERE user_projects.user_id = %s

    """, (manager_id,))

    projects = cur.fetchall()

    # -------------------------
    # PROJECT IDS
    # -------------------------

    project_ids = [project[0] for project in projects]

    # -------------------------
    # HANDLE EMPTY PROJECTS
    # -------------------------

    if not project_ids:

        return render_template(
            'manager_dashboard.html',
            projects=[],
            tickets=[],
            total_tickets=0,
            open_tickets=0,
            in_progress_tickets=0,
            resolved_tickets=0
        )

    placeholders = ','.join(['%s'] * len(project_ids))

    # -------------------------
    # TOTAL TICKETS
    # -------------------------

    cur.execute(f"""

        SELECT COUNT(*)

        FROM tickets

        WHERE project_id IN ({placeholders})

    """, tuple(project_ids))

    total_tickets = cur.fetchone()[0]

    # -------------------------
    # OPEN TICKETS
    # -------------------------

    cur.execute(f"""

        SELECT COUNT(*)

        FROM tickets

        WHERE status='Open'
        AND project_id IN ({placeholders})

    """, tuple(project_ids))

    open_tickets = cur.fetchone()[0]

    # -------------------------
    # IN PROGRESS
    # -------------------------

    cur.execute(f"""

        SELECT COUNT(*)

        FROM tickets

        WHERE status='In Progress'
        AND project_id IN ({placeholders})

    """, tuple(project_ids))

    in_progress_tickets = cur.fetchone()[0]

    # -------------------------
    # RESOLVED
    # -------------------------

    cur.execute(f"""

        SELECT COUNT(*)

        FROM tickets

        WHERE status='Resolved'
        AND project_id IN ({placeholders})

    """, tuple(project_ids))

    resolved_tickets = cur.fetchone()[0]

    # -------------------------
    # RECENT TICKETS
    # -------------------------

    query = f"""

        SELECT
            tickets.ticket_id,
            tickets.ticket_number,
            tickets.title,
            tickets.priority,
            tickets.status,
            users.full_name,
            projects.project_name

        FROM tickets

        LEFT JOIN users
        ON tickets.assigned_to = users.id

        JOIN projects
        ON tickets.project_id = projects.id

        WHERE tickets.project_id IN ({placeholders})

    """

    params = list(project_ids)

    # -------------------------
    # SEARCH FILTER
    # -------------------------

    if search:

        query += """

            AND (

                tickets.ticket_number LIKE %s
                OR tickets.title LIKE %s
                OR tickets.status LIKE %s
                OR tickets.priority LIKE %s
                OR users.full_name LIKE %s
                OR projects.project_name LIKE %s

            )

        """

        params.extend([

            f"%{search}%",
            f"%{search}%",
            f"%{search}%",
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"

        ])

    # -------------------------
    # STATUS FILTER
    # -------------------------

    if status_filter:

        query += """

            AND tickets.status = %s

        """

        params.append(status_filter)

    # -------------------------
    # ORDERING
    # -------------------------

    query += """

        ORDER BY tickets.created_at DESC

        LIMIT 10

    """

    cur.execute(query, tuple(params))

    tickets = cur.fetchall()

    cur.close()

    return render_template(
        'manager_dashboard.html',
        search=search,
        status_filter=status_filter,
        projects=projects,
        tickets=tickets,
        total_tickets=total_tickets,
        open_tickets=open_tickets,
        in_progress_tickets=in_progress_tickets,
        resolved_tickets=resolved_tickets
    )

@app.route('/manager-reports')
def manager_reports():

    if session.get('role') != 'manager':
        return redirect('/')

    cur = mysql.connection.cursor()

    manager_id = session.get('user_id')

    # MANAGER PROJECTS
    cur.execute("""

        SELECT project_id
        FROM user_projects
        WHERE user_id = %s

    """, (manager_id,))

    project_ids = [row[0] for row in cur.fetchall()]

    if not project_ids:

        return render_template(
            'manager_reports.html',
            status_data=[],
            priority_data=[],
            project_data=[]
        )

    placeholders = ','.join(['%s'] * len(project_ids))

    # TOTAL TICKETS
    cur.execute(f"""

        SELECT COUNT(*)

        FROM tickets

        WHERE project_id IN ({placeholders})

    """, tuple(project_ids))

    total_tickets = cur.fetchone()[0]

    # OPEN TICKETS
    cur.execute(f"""

        SELECT COUNT(*)

        FROM tickets

        WHERE status='Open'
        AND project_id IN ({placeholders})

    """, tuple(project_ids))

    open_tickets = cur.fetchone()[0]

    # IN PROGRESS
    cur.execute(f"""

        SELECT COUNT(*)

        FROM tickets

        WHERE status='In Progress'
        AND project_id IN ({placeholders})

    """, tuple(project_ids))

    in_progress_tickets = cur.fetchone()[0]

    # RESOLVED
    cur.execute(f"""

        SELECT COUNT(*)

        FROM tickets

        WHERE status='Resolved'
        AND project_id IN ({placeholders})

    """, tuple(project_ids))

    resolved_tickets = cur.fetchone()[0]

    # STATUS REPORT
    cur.execute(f"""

        SELECT status, COUNT(*)

        FROM tickets

        WHERE project_id IN ({placeholders})

        GROUP BY status

    """, tuple(project_ids))

    status_data = cur.fetchall()

    # PRIORITY REPORT
    cur.execute(f"""

        SELECT priority, COUNT(*)

        FROM tickets

        WHERE project_id IN ({placeholders})

        GROUP BY priority

    """, tuple(project_ids))

    priority_data = cur.fetchall()

    # PROJECT REPORT
    cur.execute(f"""

        SELECT projects.project_name,
               COUNT(tickets.ticket_id)

        FROM tickets

        JOIN projects
        ON tickets.project_id = projects.id

        WHERE tickets.project_id IN ({placeholders})

        GROUP BY projects.project_name

    """, tuple(project_ids))

    project_data = cur.fetchall()

    cur.close()

    critical_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0

    for row in priority_data:
        if row[0] == 'Critical':
            critical_count = row[1]
        elif row[0] == 'High':
            high_count = row[1]
        elif row[0] == 'Medium':
            medium_count = row[1]
        elif row[0] == 'Low':
            low_count = row[1]

    return render_template(
        'manager_reports.html',
        total_tickets=total_tickets,
        open_tickets=open_tickets,
        in_progress_tickets=in_progress_tickets,
        resolved_tickets=resolved_tickets,
        status_data=status_data,
        priority_data=priority_data,
        project_data=project_data,
        critical_count=critical_count,
        high_count=high_count,
        medium_count=medium_count,
        low_count=low_count
    )

@app.route('/customer-dashboard')
def customer_dashboard():

    # -------------------------
    # CUSTOMER SESSION CHECK
    # -------------------------

    if session.get('role') != 'customer':

        return redirect('/')

    cur = mysql.connection.cursor()

    customer_id = session.get('user_id')

    search = request.args.get('search', '')

    status_filter = request.args.get('status', '')

    # -------------------------
    # CUSTOMER PROJECT
    # -------------------------

    cur.execute("""

        SELECT project_id

        FROM user_projects

        WHERE user_id = %s

    """, (customer_id,))

    result = cur.fetchone()

    if not result:

        return render_template(

            'customer_dashboard.html',

            tickets=[],
            total_tickets=0,
            open_tickets=0,
            in_progress_tickets=0,
            resolved_tickets=0

        )

    project_id = result[0]

    # -------------------------
    # TOTAL TICKETS
    # -------------------------

    cur.execute("""

        SELECT COUNT(*)

        FROM tickets

        WHERE project_id = %s

    """, (project_id,))

    total_tickets = cur.fetchone()[0]

    # -------------------------
    # OPEN TICKETS
    # -------------------------

    cur.execute("""

        SELECT COUNT(*)

        FROM tickets

        WHERE status='Open'
        AND project_id = %s

    """, (project_id,))

    open_tickets = cur.fetchone()[0]

    # -------------------------
    # IN PROGRESS
    # -------------------------

    cur.execute("""

        SELECT COUNT(*)

        FROM tickets

        WHERE status='In Progress'
        AND project_id = %s

    """, (project_id,))

    in_progress_tickets = cur.fetchone()[0]

    # -------------------------
    # RESOLVED
    # -------------------------

    cur.execute("""

        SELECT COUNT(*)

        FROM tickets

        WHERE status='Resolved'
        AND project_id = %s

    """, (project_id,))

    resolved_tickets = cur.fetchone()[0]

    # -------------------------
    # RECENT TICKETS
    # -------------------------

    query = """

        SELECT
            tickets.ticket_id,
            tickets.ticket_number,
            tickets.title,
            tickets.priority,
            tickets.status,
            users.full_name

        FROM tickets

        LEFT JOIN users
        ON tickets.assigned_to = users.id

        WHERE tickets.project_id = %s

    """

    params = [project_id]

    # SEARCH
    if search:

        query += """

            AND (

                tickets.ticket_number LIKE %s
                OR tickets.title LIKE %s
                OR tickets.status LIKE %s
                OR tickets.priority LIKE %s
                OR users.full_name LIKE %s

            )

        """

        params.extend([

            f"%{search}%",
            f"%{search}%",
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"

        ])

    # STATUS FILTER
    if status_filter:

        query += """

            AND tickets.status = %s

        """

        params.append(status_filter)

    query += """

        ORDER BY tickets.created_at DESC

        LIMIT 10

    """

    cur.execute(query, tuple(params))

    tickets = cur.fetchall()

    cur.close()

    return render_template(

        'customer_dashboard.html',

        tickets=tickets,

        search=search,

        status_filter=status_filter,

        total_tickets=total_tickets,

        open_tickets=open_tickets,

        in_progress_tickets=in_progress_tickets,

        resolved_tickets=resolved_tickets

    )

@app.route('/forgot-password')
def forgot_password():

    return render_template(
        'forgot_password.html'
    )

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename
    )
#------------------------------
if __name__ == '__main__':
    app.run(debug=True)
