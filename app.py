from flask import Flask, render_template, request, redirect, send_from_directory, session, url_for
import os

app = Flask(_name_)
app.secret_key = 'supersecretkey'  # Change this

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Simple login system
USERNAME = 'admin'
PASSWORD = '1234'  # Change this

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            return redirect('/')

    files = os.listdir(UPLOAD_FOLDER)
    return render_template('index.html', files=files)

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete/<filename>')
def delete_file(filename):
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/login')

if _name_ == '_main_':
    app.run(debug=True)
