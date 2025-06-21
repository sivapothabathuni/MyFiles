from flask import Flask, render_template, request, redirect, send_from_directory, session, url_for
import os
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Simple login config
USERNAME = 'admin'
PASSWORD_FILE = 'config.json'

# Load or create initial password
def load_password():
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE) as f:
            data = json.load(f)
            return data.get('password', '1234')
    else:
        save_password('1234')
        return '1234'

def save_password(new_password):
    with open(PASSWORD_FILE, 'w') as f:
        json.dump({'password': new_password}, f)

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
        if request.form['username'] == USERNAME and request.form['password'] == load_password():
            session['logged_in'] = True
            return redirect('/')
        else:
            return render_template('login.html', error="Invalid credentials.")
    return render_template('login.html')

@app.route('/change-password', methods=['POST'])
def change_password():
    if 'logged_in' not in session:
        return redirect('/login')

    current = request.form['current_password']
    new = request.form['new_password']
    confirm = request.form['confirm_password']

    if current != load_password():
        return render_template('login.html', error="Current password is incorrect.")

    if new != confirm:
        return render_template('login.html', error="Passwords do not match.")

    save_password(new)
    return render_template('login.html', message="Password changed successfully.")

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/login')

if __name__ == '_main':  # <-- Fixed: should be 'main_'
    app.run(debug=True)
