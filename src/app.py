
from flask import Flask, render_template, request, redirect, url_for, flash, Response, send_file
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required
from fpdf import FPDF

from config import config

# Models:
from models.ModelUser import ModelUser

# Entities:
from models.entities.User import User

app = Flask(__name__)

csrf = CSRFProtect()
db = MySQL(app)
login_manager_app = LoginManager(app)


@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db, id)


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # print(request.form['username'])
        # print(request.form['password'])
        user = User(0, request.form['username'], request.form['password'])
        logged_user = ModelUser.login(db, user)
        if logged_user != None:
            if logged_user.password:
                login_user(logged_user)
                return redirect(url_for('home'))
            else:
                flash("Invalid password...")
                return render_template('auth/login.html')
        else:
            flash("User not found...")
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']
        cur = db.connection.cursor()
        # user_exist = cur.execute('SELECT username FROM user')
        # # if user_exist != username:
        cur.execute('INSERT INTO user (username, password, fullname) VALUES (%s, %s, %s)', 
        (username, password, fullname))
        db.connection.commit()
        flash('Usuario creado con éxito')
        redirect(url_for('register'))
        # else:
        #     flash('Usuario ya existente')    
    return render_template('./auth/register.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    cur = db.connection.cursor()
    cur.execute('SELECT fullname FROM user')
    data = cur.fetchall()
    return render_template('./home.html', user = data)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/products', methods=['GET', 'POST'])
def products():
    cur = db.connection.cursor()
    cur.execute('SELECT * FROM products')
    data = cur.fetchall()

    if request.method == 'POST':
        name = request.form['name']
        stock = request.form['stock']
        value = request.form['value']
        cur = db.connection.cursor()
        cur.execute('INSERT INTO products (name, stock, value) VALUES (%s, %s, %s)', 
        (name, stock, value))
        db.connection.commit()
        flash('Producto registrado con éxito')
        redirect(url_for('products'))

    return render_template('products.html', product = data)



def status_401(error):
    return redirect(url_for('login'))


def status_404(error):
    return render_template('404.html'), 404

@app.route('/')
def download_report():
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_font('Times', 'B', 12)
    pdf.set_fill_color(0, 0, 255)
    pdf.cell(190, 10, "REPORTE GENERAL DE PRODUCTOS",10, 25,"C")
    pdf.cell(8, 10, "PRODUCTO", 1, 0)
    pdf.cell(50, 10, "CANTIDAD", 1, 0)
    pdf.cell(45, 10, "VALOR", 1, 0)

    cursor = db.connection.cursor()
    cursor.execute("SELECT * FROM products")
    product = cursor.fetchall() 

    for products in product:
        name = products[1] 
        stock = products[2]  
        value = products[3] 
        pdf.cell(8, 10,"producto=%s" % (name), 1, 0)
        pdf.cell(50, 10,"cantidad=%s" % (stock), 1, 0)
        pdf.cell(45, 10,"valor=%s" % (value) , 1, 0)

        return pdf.output(name = "reporte_productos.pdf",dest='F')

if __name__ == '__main__':
    app.config.from_object(config['development'])
    #csrf.init_app(app)
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run()
