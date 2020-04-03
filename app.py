from flask import Flask, render_template, redirect, url_for, request, jsonify, session, abort
import sqlite3 
import json
from datetime import date

app = Flask(__name__)
app.secret_key = 'mz*.5"tjXQ97x{h'

database = 'lmsdatabase.db'

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
            cur.execute("SELECT * FROM ISS_STU WHERE roll_no=?", (id,))
            rows = cur.fetchall()
            for row in rows:
                obj = get_issue_obj(row)
                data.append(obj)
        return jsonify({"user": user, "books": data})
    else:
        abort(404)

def get_issue_obj(row):
    print(row)

def get_student_obj(row):
    obj = {}
    obj['roll_no'] = row[0]
    obj['name'] = row[1]
    obj['contact'] = row[2]
    obj['is_fac'] = row[3]
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
            cur.execute("SELECT * FROM CUSTOMERS")
            rows = cur.fetchall()
            for row in rows:
                obj = get_student_obj(row)
                data.append(obj)
        return jsonify({"data": data})
    else:
        abort(404)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')

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
        return render_template('dashboard.html', user=username, is_admin=is_admin, books=data)
    else:
        return redirect(url_for('login'))

if __name__== "__main__":
    app.run(debug=True)