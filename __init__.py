from flask import Flask, render_template, request, session, url_for, redirect, flash
import datetime
import sqlite3 as sql
from flask_user import current_user, UserManager, UserMixin
from passlib.hash import sha256_crypt as sha256_crypt
import gc
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = "EbruBETÜL"

conn = sql.connect('veritabani.db')
conn.execute("""CREATE TABLE IF NOT EXISTS kullanicilar (
	TCNo varchar(11) PRIMARY KEY NOT NULL, 
	Ad varchar(50) NOT NULL, 
	Soyad varchar(50) NOT NULL, 
	TelNo varchar(20), 
	Email varchar(50) NOT NULL, 
	Bakiye INT, 
	Bonus INT, 
	Parola varchar(20) NOT NULL, 
	Rol varchar(2) NOT NULL
	)
""")

conn.execute("""CREATE TABLE IF NOT EXISTS personeller (
	TCNo varchar(11) PRIMARY KEY NOT NULL,
	Ad varchar(50) NOT NULL,
	Soyad varchar(50) NOT NULL,
	TelNo varchar(20) NOT NULL,
	Email varchar(50) NOT NULL,
	Parola varchar(20) NOT NULL,
	Cinsiyet BOOLEAN NOT NULL,
	Rol varchar(2) NOT NULL
	)
""")	

conn.execute("""CREATE TABLE IF NOT EXISTS biletler (
	BiletID INT AUTO_INCREMENT PRIMARY_KEY,
	TCNo nvarchar(11) NOT NULL,
	KoltukID nvarchar(11) NOT NULL,
	BagajNo nvarchar(11),
	UcusID nvarchar(11), 
	CONSTRAINT fk_user_tc FOREIGN KEY (TCNo) REFERENCES kullanicilar(TCNo),
	CONSTRAINT fk_ucus FOREIGN KEY (UcusID) REFERENCES ucuslar(UcusID),
	CONSTRAINT fk_koltuk FOREIGN KEY (KoltukID) REFERENCES koltuklar(KoltukID)
	)
""") 

conn.execute("""CREATE TABLE IF NOT EXISTS sepet (
	SepetID INT AUTO_INCREMENT PRIMARY KEY,
	TCNo varchar(11),
	KoltukID varchar(11),
	UcusID varchar(11),	
	CONSTRAINT fk_user_tc2 FOREIGN KEY (TCNo) REFERENCES kullanicilar(TCNo),
	CONSTRAINT fk_ucus2 FOREIGN KEY (UcusID) REFERENCES ucuslar(UcusID),
	CONSTRAINT fk_koltuk2 FOREIGN KEY (KoltukID) REFERENCES koltuklar(KoltukID)
	)
""")

conn.execute("""CREATE TABLE IF NOT EXISTS ucuslar (
	UcusID INT AUTO_INCREMENT PRIMARY KEY,
	KalkisYeri varchar(30),
	InisYeri nvarchar(30),
	Fiyat INT,
	Tarih datetime,
	KoltukID varchar(11),
	CONSTRAINT fk_koltuk2 FOREIGN KEY (KoltukID) REFERENCES koltuklar(KoltukID)
	)
""")

conn.execute("""CREATE TABLE IF NOT EXISTS koltuk (
	UcusID INT AUTO_INCREMENT PRIMARY KEY,
	Koltuk1 INT,
	Koltuk2 INT,
	Koltuk3 INT,
	Koltuk4 INT,
	Koltuk5 INT,
	Koltuk6 INT,
	Koltuk7 INT,
	Koltuk8 INT,
	Koltuk9 INT,
	Koltuk10 INT,
	CONSTRAINT fk_ucus3 FOREIGN KEY (UcusID) REFERENCES ucuslar(UcusID)
	)
""")

conn.commit()
conn.close()

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Öncelikle giriş yapmalısınız!!!")
            return redirect(url_for('login'))
    return wrap

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get('admin'):
            return f(*args, **kwargs)
        else:
            flash("Bu sayfa için yetkiniz bulunmamaktadır.")
            return redirect(url_for('home'))
    return wrap

@app.route('/')
def home():
    con = sql.connect("veritabani.db")
    con.row_factory= sql.Row

    cur= con.cursor()
    cur.execute("select * from kullanicilar")

    rows= cur.fetchall()
    return render_template("index.html", kayitlar = rows)

@app.route('/kayit/')
def kayit():
    return render_template("kayit.html")

@app.route('/giris/')
def giris():
    return render_template("giris.html", mesaj = "Kayıt eklendi")

@app.route('/kayit_ekle', methods = ['POST', 'SET'])
def kayit_ekle():
    if request.method == 'POST':
        try:
            TC = request.form['TC']
            Ad = request.form['Ad']
            Soyad = request.form['Soyad']
            Email = request.form['Email']
            Tel = request.form['Tel']
            Parola = sha256_crypt.hash(str(request.form['Parola']))
            Bakiye = 0
            Bonus = 0
            Rol = 0

            with sql.connect("veritabani.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO kullanicilar (TCNo,Ad,Soyad,TelNo,Email,Bakiye,Bonus,Parola,Rol) values (?,?,?,?,?,?,?,?,?)", (TC,Ad,Soyad,Tel,Email,str(Bakiye),str(Bonus),Parola,str(Rol)))

                con.commit()
                msg = "Kayıt eklendi"
        except:
            con.rollback()
            msg = "Kayıt eklenirken hata oluştu"
        finally:
            con.close()
            return render_template("giris.html", mesaj = msg)
    return render_template('/home')

@app.route('/login/', methods=['GET', 'POST'])
def login():
	conn = sql.connect("veritabani.db")
	c= conn.cursor()
	if request.method == 'POST':
		c.execute("""SELECT * FROM kullanicilar WHERE TCNo = '%s'"""%(request.form['TC']))
        
		result=c.fetchall()
		tc= result[0][0]
		pas= result[0][7]
		role= result[0][8]
		if sha256_crypt.verify(request.form['Parola'],pas):
			session['logged_in']=True
			session['username']=tc
			if role==0:
				session['admin']=False
			elif role==1:
				session['admin']=True
			else:
				session['admin']=False
			gc.collect()
			flash("Başarıyla giriş yaptınız")
			return redirect(url_for('home'))
		else:
			flash("Hatalı giriş yaptınız. Tekrar deneyiniz.")
			return render_template("index.html")
	return

@app.route('/hesabim')
def hesabim():
    con = sql.connect("veritabani.db")
    con.row_factory= sql.Row

    cur= con.cursor()
    cur.execute("SELECT * FROM kullanicilar WHERE TCNo = ?",[session['username']])

    rows= cur.fetchone()
    return render_template("hesabim.html", hesapbilgileri = rows)

@app.route("/admin")
@login_required
@admin_required
def adminSayfa():
	return render_template("admin.html")

@app.route("/ucus_ekle")
def ucus_ekle():
    return render_template("ucus_ekle.html")

@app.route("/ucusekle", methods = ['POST', 'SET'])
def ucusekle():
	conn = sql.connect('veritabani.db')
	c=conn.cursor()
	if request.method == 'POST':
		try:
			with sql.connect("veritabani.db") as cn:
				cn_cur = cn.cursor()
				cn_cur.execute("""INSERT INTO koltuk VALUES (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)""")
				cn.commit()
			KalkisYeri = request.form['kalkisYeri']
			InisYeri = request.form['inisYeri']
			Fiyat = request.form['fiyat']
			Tarih = request.form['tarih']
			sonID = c.lastrowid

			with sql.connect("veritabani.db") as con:
				cur = con.cursor()
				cur.execute("INSERT INTO ucuslar (KalkisYeri,InisYeri,Fiyat,Tarih,KoltukID) values (?,?,?,?,?)", (KalkisYeri,InisYeri,Fiyat,Tarih,sonID))

				con.commit()
		except:
			con.rollback()
			cn.rollback()
		finally:
			cn.close()
			con.close()
			return render_template("index.html")
	return render_template('/home')

@app.route("/ucusduzenle")
def ucusduzenle():
	asdasdsa

@app.route("/ucussil")
def ucussil():
	asdasdasd

@app.route("/logout/")
@login_required
def logout():
	session.clear()
	flash("Başarı ile çıkış yaptınız.")
	gc.collect()
	return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)