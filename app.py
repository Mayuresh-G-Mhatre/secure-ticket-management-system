import os
from werkzeug.utils import secure_filename
from flask import send_from_directory
from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# -------------------------
# SECRET KEY
# -------------------------

app.secret_key = 'stms_secret_key'

# -------------------------
# MYSQL CONFIGURATION
# -------------------------

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '<password>'
app.config['MYSQL_DB'] = 'stms_db'

mysql = MySQL(app)

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

    cur = mysql.connection.cursor()

    # -------------------------
    # FETCH / SEARCH TICKETS
    # -------------------------

    if search:

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
    AND (
        tickets.ticket_number LIKE %s
        OR tickets.title LIKE %s
    )

    ORDER BY tickets.created_at DESC
        """

        search_term = f"%{search}%"

        cur.execute(query, (search_term, search_term))

    else:

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

    ORDER BY tickets.created_at DESC
        """

        cur.execute(query)

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
    total_tickets=total_tickets,
    open_tickets=open_tickets,
    in_progress_tickets=in_progress_tickets,
    resolved_tickets=resolved_tickets,
    search=search,
    active_page='all_tickets'
)

@app.route('/create-ticket', methods=['GET', 'POST'])
def create_ticket():
    
    cur = mysql.connection.cursor()

    # Generate next ticket number
    cur.execute("SELECT COUNT(*) FROM tickets")
    count = cur.fetchone()[0] + 1

    next_ticket_number = f"ST{1000 + count}"

    if request.method == 'POST':

        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        priority = request.form['priority']
        attachment = request.files['attachment']

        filename = None

        if attachment and attachment.filename != '':
            filename = secure_filename(attachment.filename)
            attachment.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    filename
                )
            )
        
        ticket_number = next_ticket_number

        query = """
            INSERT INTO tickets
            (ticket_number, title, description,
             category, priority, status,
             created_by, assigned_to,attachment)

            VALUES (%s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s)
        """

        values = (
            ticket_number,
            title,
            description,
            category,
            priority,
            'Open',
            4,
            2,
            filename
        )

        cur.execute(query, values)

        mysql.connection.commit()

        cur.close()

        return redirect('/admin-dashboard')

    return render_template(
        'create_ticket.html',
        next_ticket_number=next_ticket_number,
        full_name=session.get('full_name')
    )

@app.route('/ticket/<int:ticket_id>')
def view_ticket(ticket_id):

    cur = mysql.connection.cursor()

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
        engineers=engineers
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

        ORDER BY tickets.created_at DESC
    """

    cur.execute(query)

    tickets = cur.fetchall()

    cur.close()

    return render_template(
    'archived_tickets.html',
    tickets=tickets,
    active_page='archived_tickets'
)

@app.route('/reports')
def reports():

    cur = mysql.connection.cursor()

    # -------------------------
    # TOTAL TICKETS
    # -------------------------

    cur.execute("SELECT COUNT(*) FROM tickets")
    total_tickets = cur.fetchone()[0]

    # -------------------------
    # OPEN
    # -------------------------

    cur.execute("""
        SELECT COUNT(*)
        FROM tickets
        WHERE status='Open'
    """)

    open_tickets = cur.fetchone()[0]

    # -------------------------
    # IN PROGRESS
    # -------------------------

    cur.execute("""
        SELECT COUNT(*)
        FROM tickets
        WHERE status='In Progress'
    """)

    in_progress_tickets = cur.fetchone()[0]

    # -------------------------
    # RESOLVED
    # -------------------------

    cur.execute("""
        SELECT COUNT(*)
        FROM tickets
        WHERE status='Resolved'
    """)

    resolved_tickets = cur.fetchone()[0]

    # -------------------------
    # CLOSED
    # -------------------------

    cur.execute("""
        SELECT COUNT(*)
        FROM tickets
        WHERE status='Closed'
    """)

    closed_tickets = cur.fetchone()[0]

    # -------------------------
    # CRITICAL TICKETS
    # -------------------------

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
        active_page='reports'
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

    query = """
        SELECT
            id,
            full_name,
            username,
            email,
            role
        FROM users
        ORDER BY id DESC
    """

    cur.execute(query)

    users = cur.fetchall()

    cur.close()

    return render_template(
        'manage_users.html',
        users=users,
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

@app.route('/engineer-dashboard')
def engineer_dashboard():
    return "<h1>Engineer Dashboard</h1>"

@app.route('/manager-dashboard')
def manager_dashboard():
    return "<h1>Manager Dashboard</h1>"

@app.route('/customer-dashboard')
def customer_dashboard():
    return "<h1>Customer Dashboard</h1>"

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename
    )
#------------------------------
if __name__ == '__main__':
    app.run(debug=True)
