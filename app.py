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
app.config['MYSQL_PASSWORD'] = 'Mac@2520'
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
    cur = mysql.connection.cursor()

    query = """
       SELECT ticket_id, ticket_number, title, priority, status
        FROM tickets
        ORDER BY created_at DESC
    """

    cur.execute(query)

    tickets = cur.fetchall()

    cur.close()

    return render_template(
        'admin_dashboard.html',
        tickets=tickets
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

    query = """
        SELECT *
        FROM tickets
        WHERE ticket_id = %s
    """

    cur.execute(query, (ticket_id,))

    ticket = cur.fetchone()

    cur.close()

    return render_template(
        'view_ticket.html',
        ticket=ticket
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