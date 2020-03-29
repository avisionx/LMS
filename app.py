from flask import Flask, render_template, redirect, url_for, request, jsonify, session
import sqlite3 
import json

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
        obj['total'] = row[9]
        obj['issued'] = row[10]
    return obj


@app.route('/', methods=['GET'])
def index():
    data = []
    con = create_connection(database)
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM BOOKS")
        rows = cur.fetchall()
        for row in rows:
            obj = get_book_obj(row, desc=False)
            data.append(obj)
    return render_template('index.html', books=data)

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
        cur.execute("SELECT * FROM USERS")
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
        return render_template('dashboard.html', user=username)
    else:
        return redirect(url_for('login'))

if __name__== "__main__":
    app.run(debug=True)