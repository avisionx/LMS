import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import shutil 
from flask import Flask, render_template, redirect, url_for, request, jsonify, session, abort
import sqlite3 
import json
from datetime import date, datetime
import numpy as np

app = Flask(__name__)
app.secret_key = 'mz*.5"tjXQ97x{h'

database = 'lmsdatabase.db'

statImg = [
    
]

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn

def get_book_obj(row, desc=True):
    obj = {}
    obj['_id'] = row[0]
    obj['title'] = row[1]
    obj['thumbnailUrl'] = row[2]
    authors = row[5]
    authors = authors.replace("\\", "")
    authors = authors.split(",")
    obj['authors'] = authors
    if(desc):
        obj['shortDescription'] = row[3]
        obj['longDescription'] = row[4]
        obj['isbn'] = row[6]
        obj['categories'] = row[7]
        obj['rack'] = row[8]
        obj['issued'] = row[9]
    return obj

@app.route('/', methods=['GET'])
def index():
    username = None
    if 'username' in session:
        username = session['username']
    data = []
    con = create_connection(database)
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM BOOKS ORDER BY TITLE")
        rows = cur.fetchall()
        for row in rows:
            obj = get_book_obj(row, desc=False)
            data.append(obj)
    return render_template('index.html', books=data, user=username)

@app.route('/book/<id>', methods=['GET'])
def get_book(id):
    con = create_connection(database)
    obj = {}
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM BOOKS WHERE _id=?", (id,))
        row = cur.fetchone()
        obj = get_book_obj(row)
    return jsonify({"data": obj})
    
@app.route('/book/remove/<id>', methods=['GET'])
def book_remove(id):
    if 'username' in session:
        username = session['username']
        id = int(id[1:-1])
        con = create_connection(database)
        with con:
            cur = con.cursor()
            cur.execute("Select * from books where _id=?", (id,))
            row = cur.fetchone()
            if(row):
                cur.execute("DELETE FROM BOOKS WHERE _id=?", (id,))
                cur.execute("DELETE FROM ISS_STU WHERE _id=?", (id,))
                message = "Book deleted successfully!"
            else:
                message = "No such book found!"
        return render_template('book_message.html', message=message, user=username)
    else:
        abort(404)
    
@app.route('/user/remove/<id>', methods=['GET'])
def user_remove(id):
    if 'username' in session:
        username = session['username']
        con = create_connection(database)
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM CUSTOMERS WHERE roll_no=?", (id,))
            row = cur.fetchone()
            if(row):
                cur.execute("DELETE FROM CUSTOMERS WHERE roll_no=?", (id,))
                cur.execute("DELETE FROM ISS_STU WHERE roll_no=?", (id,))
                cur.execute("UPDATE BOOKS SET issued=? WHERE issued=?", ('none', id,))
                message = "User deleted successfully!"
            else:
                message = "No such user found!"
        return render_template('book_message.html', message=message, user=username)
    else:
        abort(404)


@app.route('/staff/remove/<id>/', methods=['GET'])
def staff_remove(id):
    if 'username' in session:
        username = session['username']
        con = create_connection(database)
        id = id + "@fiveteen.com"
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM STAFF WHERE username=?", (id,))
            row = cur.fetchone()
            if(row):
                cur.execute("DELETE FROM STAFF WHERE username=?", (id,))
                message = "Staff deleted successfully!"
            else:
                message = "No such staff found!"
        return render_template('book_message.html', message=message, user=username)
    else:
        abort(404)

@app.route('/book/add/', methods=['GET', 'POST'])
def book_add():
    if 'username' in session:
        username = session['username']
        message = None
        try:
            if request.method == 'POST':
                title = request.form.get('title')
                isbn = request.form.get('isbn')
                imgurl = request.form.get('imgurl')
                shortDescription = request.form.get('shortDescription')
                longDescription = request.form.get('longDescription')
                authors = str(request.form.get('authors').split(","))[1:-1].replace("'", "")
                categories = str(request.form.get('categories').split(","))[1:-1].replace("'", "")
                rack = title[0] + '-' + isbn[0:4]
                
                con = create_connection(database)
                with con:
                    cur = con.cursor()
                    cur.execute("INSERT INTO BOOKS(title, thumbnailUrl, shortDescription, longDescription, authors, isbn, categories, rack, issued) VALUES(?,?,?,?,?,?,?,?,?)", (title, imgurl, shortDescription, longDescription, authors, isbn, categories, rack, 'none'))
                message = "Book added successfully!"
        except:
            message = "Error adding new book!"
        return render_template('book_add.html', user=username, message=message)
    else:
        abort(404)

@app.route('/user/add/', methods=['GET', 'POST'])
def user_add():
    if 'username' in session:
        username = session['username']
        message = None
        try:
            if request.method == 'POST':

                roll_no = request.form.get('roll_no')
                contact = request.form.get('contact')
                name = request.form.get('name')
                is_fac = request.form.get('is_fac')
                if(not is_fac):
                    is_fac = 0
                con = create_connection(database)
                with con:
                    cur = con.cursor()
                    cur.execute("INSERT INTO CUSTOMERS(roll_no, name, contact, is_fac) VALUES(?,?,?,?)", (roll_no, name, contact, is_fac))
                message = "User added successfully!"
        except:
            message = "Error adding new User!"
        return render_template('user_add.html', user=username, message=message)
    else:
        abort(404)


@app.route('/staff/add/', methods=['GET', 'POST'])
def staff_add():
    if 'username' in session:
        username = session['username']
        message = None
        try:
            if request.method == 'POST':

                usernameN = request.form.get('username')
                password = request.form.get('password')
                is_admin = request.form.get('is_admin')
                if(not is_admin):
                    is_admin = 0
                con = create_connection(database)
                with con:
                    cur = con.cursor()
                    cur.execute("INSERT INTO STAFF(username, password, is_admin) VALUES(?,?,?)", (usernameN, password, is_admin))
                message = "Staff added successfully!"
        except:
            message = "Error adding new Staff!"
        return render_template('staff_add.html', user=username, message=message)
    else:
        abort(404)

@app.route('/makecharts', methods=['GET'])
def make_charts():
    
    global statImg

    shutil.rmtree("./static/img/stats/")
    os.mkdir("./static/img/stats/")
    
    statImg = []
    imgName = ""
    if 'username' in session:
        username = session['username']
        con = create_connection(database)
        message = "Charts have been reloaded!"
        with con:
            cur = con.cursor()
            
            cur.execute("select count(*), issue_date from ISS_STU group by issue_date")
            rows = cur.fetchall()
            X = []
            Y = []
            now = datetime.now().time()
            timestamp = str(now).replace(":", "-").replace(".", "-")
            imgName = timestamp + 'issue.png'
            if(len(rows) > 0):
                statImg.append(imgName)
                for row in rows:
                    Y.append(row[0])
                    X.append(row[1])
                plt.bar(X, Y, color="orange")
                plt.yticks(np.arange(min(Y) - 1, max(Y) + 1, step=1))
                plt.xlabel("Dates")
                plt.ylabel("No of Book")
                plt.title("Books issued per day")
                plt.savefig('./static/img/stats/' + imgName) 
                plt.close()
        with con:
            cur = con.cursor()
            cur.execute("select count(*), return_date from ISS_STU where return_date != '' group by return_date")
            rows = cur.fetchall()
            X = []
            Y = []
            now = datetime.now().time()
            timestamp = str(now).replace(":", "-").replace(".", "-")
            imgName = timestamp + 'return.png'
            if(len(rows) > 0):
                statImg.append(imgName)
                for row in rows:
                    Y.append(row[0])
                    X.append(row[1])
                plt.bar(X, Y, color="green")
                plt.yticks(np.arange(min(Y) - 1, max(Y) + 1, step=1))
                plt.xlabel("Dates")
                plt.ylabel("No of Book")
                plt.title("Books returned per day")
                plt.savefig('./static/img/stats/' + imgName) 
                plt.close() 
        with con:
            cur = con.cursor()
            cur.execute("select avg(fine), max(fine), sum(fine) from ISS_STU")
            rows = cur.fetchone()
            try:
                f = rows[0] > 0
                Y = rows
                X = ['Average', 'Max', 'Total']
                now = datetime.now().time()
                timestamp = str(now).replace(":", "-").replace(".", "-")
                imgName = timestamp + 'fine.png'
                statImg.append(imgName)
                plt.bar(X, Y, color="green")
                plt.ylabel("Fine in Rs.")
                plt.title("Fine statistics")
                plt.savefig('./static/img/stats/' + imgName) 
                plt.close()
            except:
                pass
        return render_template('book_message.html', user=username, message=message)
    else:
        abort(404)

@app.route('/book/issue/<bid>/<uid>', methods=['GET'])
def book_issue(bid, uid):
    if 'username' in session:
        username = session['username']
        message = ""
        con = create_connection(database)
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM CUSTOMERS WHERE roll_no=?", (uid,))
            row = cur.fetchone()
            if(row):
                today = date.today()
                cur.execute("SELECT issued from BOOKS WHERE _id=?", (bid, ))
                row = cur.fetchone()
                if(row[0] == 'none'):
                    cur.execute("UPDATE BOOKS SET issued=? WHERE _id=?", (uid, bid))
                    cur.execute("INSERT INTO ISS_STU VALUES(?, ?, ?, ?, 0)", (bid, uid, str(today), ''))
                    message = "Book issued successfully!"
                else:
                    message = "Book is unavailable right now!"
            else:
                message = "No such user exists!"
        return render_template('book_message.html', message=message, user=username)
    else:
        abort(404)


@app.route('/<fine>/<uid>/<bid>/', methods=['GET'])
def book_fine(fine, uid, bid):
    if 'username' in session:
        username = session['username']
        message = ""
        con = create_connection(database)
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM CUSTOMERS WHERE roll_no=?", (uid,))
            row = cur.fetchone()
            if(row):
                cur.execute("UPDATE ISS_STU SET fine=? WHERE _id=? and roll_no=?", (fine, bid, uid))
                message = "Fine updated successfully!"
            else:
                message = "No such user exists!"
        return render_template('book_message.html', message=message, user=username)
    else:
        abort(404)

@app.route('/book/return/<bid>/<uid>', methods=['GET'])
def book_return(bid, uid):
    if 'username' in session:
        username = session['username']
        message = ""
        con = create_connection(database)
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM CUSTOMERS WHERE roll_no=?", (uid,))
            row = cur.fetchone()
            if(row):
                today = date.today()
                cur.execute("SELECT issued from BOOKS WHERE _id=?", (bid, ))
                row = cur.fetchone()
                if(row[0] == uid):
                    cur.execute("UPDATE BOOKS SET issued=? WHERE _id=?", ('none', bid))
                    cur.execute("UPDATE ISS_STU SET return_date=? WHERE _id=? and roll_no=?", (str(today), bid, uid))
                    message = "Book returned successfully!"
                else:
                    message = "Book not returned!"
            else:
                message = "No such user exists!"
        return render_template('book_message.html', message=message, user=username)
    else:
        abort(404)

@app.route('/custdata/<id>', methods=['GET'])
def get_cust(id):
    if 'username' in session:
        username = session['username']
        con = create_connection(database)
        user = {}
        data = []
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM CUSTOMERS WHERE roll_no=?", (id,))
            row = cur.fetchone()
            user = get_student_obj(row)
        con = create_connection(database)
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM ISS_STU WHERE roll_no=? ORDER BY return_date", (id,))
            rows = cur.fetchall()
            for row in rows:
                obj = get_issue_obj(row)
                data.append(obj)
        return jsonify({"user": user, "books": data})
    else:
        abort(404)

def get_issue_obj(book_det):
    con = create_connection(database)
    book = None
    with con:
        cur = con.cursor()
        id = book_det[0]
        cur.execute("SELECT * FROM BOOKS WHERE _id=?", (id,))
        row = cur.fetchone()
        book = get_book_obj(row, desc=False)
    book['issue_date'] = book_det[2]
    book['return_date'] = book_det[3]
    book['fine_due'] = book_det[4]
    return book

def get_student_obj(row):
    obj = {}
    obj['roll_no'] = row[0]
    obj['name'] = row[1]
    obj['contact'] = row[2]
    obj['is_fac'] = row[3]
    return obj

def run_query(arg):
    con = create_connection(database)
    with con:
        return arg
        cur = con.cursor()
        cur.execute(arg)

def get_staff_obj(row):
    obj = {}
    obj['username'] = row[0]
    obj['is_admin'] = row[2]
    return obj

@app.route('/customers', methods=['GET'])
def all_customers():
    if 'username' in session:
        username = session['username']
        con = create_connection(database)
        obj = {}
        data = []
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM CUSTOMERS ORDER BY is_fac")
            rows = cur.fetchall()
            for row in rows:
                obj = get_student_obj(row)
                data.append(obj)
        return jsonify({"data": data})
    else:
        abort(404)


@app.route('/staff', methods=['GET'])
def all_staff():
    if 'username' in session:
        username = session['username']
        con = create_connection(database)
        obj = {}
        data = []
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM STAFF ORDER BY is_admin desc")
            rows = cur.fetchall()
            for row in rows:
                obj = get_staff_obj(row)
                data.append(obj)
        return jsonify({"data": data})
    else:
        abort(404)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')

def initialize_db():
    run_query("CREATE INDEX IF NOT EXISTS idx_book ON BOOK (_id);")
    run_query("CREATE INDEX IF NOT EXISTS idx_roll_no ON CUSTOMERS (roll_no);")
    run_query("CREATE INDEX IF NOT EXISTS idx_username ON STADD (username);")

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        completion = validate(username, password)
        if completion == False:
            error = 'Invalid Credentials. Please try again.'
        else:
            session['username'] = username
            return redirect(url_for('dashboard'))

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

def validate(username, password):
    con = create_connection(database)
    completion = False
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM STAFF")
        rows = cur.fetchall()
        for row in rows:
            dbUser = row[0]
            dbPass = row[1]
            if dbUser == username:
                completion=check_password(dbPass, password)
    return completion

def check_password(hashed_password, user_password):
    return hashed_password == user_password

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']
        is_admin = 0
        con = create_connection(database)
        obj = {}
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM STAFF WHERE username=?", (username,))
            row = cur.fetchone()
            try:
                is_admin = row[2]
            except:
                is_admin = 0
        data = []
        con = create_connection(database)
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM BOOKS ORDER BY TITLE")
            rows = cur.fetchall()
            for row in rows:
                obj = get_book_obj(row, desc=False)
                data.append(obj)
        return render_template('dashboard.html', user=username, is_admin=is_admin, books=data, statImg=statImg)
    else:
        return redirect(url_for('login'))

if __name__== "__main__":
    initialize_db()
    app.run(debug=True)