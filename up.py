from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL, MySQLdb
import bcrypt

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ravfurn'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


@app.route('/')
def home():
    #email = session['email']

    #cur = mysql.connection.cursor()
    #cur.execute("SELECT id_user FROM pembeli WHERE email=%s", (email,))
    #id = cur.fetchone()

    return render_template("home.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        alamat = request.form['alamat']
        password = request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO pembeli (name, email, password, alamat) VALUES (%s,%s,%s,%s)", (name, email, hash_password, alamat))
        mysql.connection.commit()
        session['name'] = request.form['name']
        session['email'] = request.form['email']
        return redirect(url_for('home'))

    return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM pembeli WHERE email=%s", (email,))
        user = curl.fetchone()
        curl.close()

        if len(user) > 0:

            # cek hash benar atau tidak
            hash = bcrypt.checkpw(password, user["password"].encode('utf-8'))

            if hash:
                session['name'] = user['name']
                session['email'] = user['email']
                name = session['name']
                return redirect(url_for('home'))
            else:
                return "Error password and email not match"
        else:
            return "Error user not found"
    else:
        return render_template("login.html")


@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    return render_template("home.html")

@app.route('/order/<id>', methods=["GET", "POST"])
def order(id):

    if request.method == 'POST':
            Id = str(id)
            nama = request.form['nama']
            jumlah = request.form['jumlah']


            cur = mysql.connection.cursor()

            cur.execute("SELECT harga FROM barang WHERE id_barang = %s",(Id,))
            data_harga = cur.fetchone()
            harga = (int(data_harga['harga']) * int(jumlah))

            email = session['email']

            cur = mysql.connection.cursor()
            cur.execute("SELECT id_user FROM pembeli WHERE email=%s", (email,))
            id_user = cur.fetchone()


            cur.execute("INSERT INTO pembelian(id_barang, id_user, jumlah, total_harga) VALUES (%s, %s, %s, %s)",
                        (Id, id_user['id_user'], jumlah, harga))
            mysql.connection.commit()


            cur.close()

            return redirect(url_for('akhir',nama=nama))

    return render_template("order.html",id=id)


@app.route('/akhir/<nama>')
def akhir(nama):

    print(nama)
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM akhir WHERE name = %s ORDER BY id_beli DESC',(nama,))
    data = cur.fetchone()
    print(data)
    nama = data['name']
    barang = data['nama_barang']
    total = data['total_harga']
    jumlah = data['jumlah']
    alamat = data['alamat']

    print(nama)
    return render_template('akhir.html',nama=nama, barang=barang, jumlah=jumlah, total=total, alamat=alamat)

if __name__ == '__main__':
    app.secret_key = "majumapan5758"
    app.run(debug=True)

