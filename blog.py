from flask import Flask,render_template,flash,redirect,url_for,session,logging,request,g
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,ValidationError,Form,validators
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from passlib.handlers.sha2_crypt import sha256_crypt
import flask_mysqldb
from functools import  wraps

#kullanıcı giriş decaratorü
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu sayfayı görüntülemeye hakkınız yok","danger")
            return redirect(url_for("login"))

    return decorated_function
#kullanıcı kayıt formu
class RegisterForm(Form):
    name = StringField("İsim Soyisim", validators=[validators.length(min = 4,max = 25)])
    username = StringField("username", validators=[validators.length(min = 5,max = 35),validators.data_required()])
    email = StringField("email", validators=[validators.Email("lütfen geçerli bir email adresi giriniz"),validators.data_required()])
    password = PasswordField("Parola:",validators=[
        validators.DataRequired(message="Lütfen bir paralo belirleyiniz"),
        validators.EqualTo(fieldname="confirm",message="Paralonız uyuşmuyor")
    ])
    confirm = PasswordField("Parolanızı Doğrulayınız")


#MAKELE FORM

class ArticleForm(Form):
    title = StringField("Makale başlığı", validators=[validators.length(min = 5,max = 100)])
    content = TextAreaField("Makale içeriği", validators=[validators.length(min=10)])

class DoComment(Form):
    comment = TextAreaField("Yorumunuz",validators=[validators.length(min = 1 )])



class LoginForm(Form):
    username = StringField("Kullanıcı Adı:")
    password = PasswordField("Parola:")

  
app=Flask(__name__)
app.secret_key = "fblog"

app.config["MYSQL HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] =""
app.config["MYSQL_DB"] = "denememfl"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"


mysql = MySQL(app)
@app.route("/")
def index():
    
    
    return render_template("index.html")

@app.route("/about")
def about():
   
   return render_template("about.html")


@app.route("/dashbord")
@login_required
def dashbord():

    cursor = mysql.connection.cursor()
    sorgu = "Select * From articles where author = %s"
    result = cursor.execute(sorgu,(session["username"],))

    if result > 0:
        articles = cursor.fetchall()
        return render_template("dashbord.html",articles = articles)
    else:
        return render_template("dashbord.html")

    return render_template("dashbord.html")

@app.route("/register",methods=["GET","POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST"and form.validate():
       

        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data)
         
        cursor = mysql.connection.cursor()
        sorgu = "Insert into tablomm (name,email,username,password) VALUES(%s,%s,%s,%s)"
        cursor.execute(sorgu,(name,email,username,password))
        mysql.connection.commit()
        cursor.close()
        flash("Başarıyla kayıt oldunuz...","success")
        
        
        return redirect(url_for("login"))
    else:
      return render_template("register.html",form=form)
#Login işlemi:
@app.route("/login", methods = ["GET","POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        username = form.username.data
        password_entered = form.password.data
        cursor = mysql.connection.cursor()
        sorgu = "Select * From tablomm where username = %s"
        result = cursor.execute(sorgu,(username,))
        if result > 0 :
            data = cursor.fetchone()
            real_password = data["password"]
            if sha256_crypt.verify(password_entered,real_password):
                flash("Başarıyla giriş yaptınız","success")
                session["logged_in"] = True
                session["username"] = username
                
                return redirect(url_for("index"))
            else:
                flash("Parolanızı yanlış girdiniz","danger")
                return redirect(url_for("login"))
        else:
            flash("Böyle bir kullanıcı bulunmuyor","danger")
            

    return render_template("login.html",form = form)

#yorum yap
@app.route("/comment", methods =["GET","POST"])
def yorumyap():
    form = DoComment(request.form)
   
  
    if request.method == "POST" and form.validate():  
       
       comment= form.comment.data
       cursor = mysql.connection.cursor()
       sorgu = "Insert into commentt (yorum) VALUES(%s)"
       cursor.execute(sorgu,(comment,))
       mysql.connection.commit()
       cursor.close()
       flash("Yorumunuz başarıyla eklendi...","success")
       return redirect(url_for("articles"))
    else:
       
       return render_template("comment.html", form = form)
555555555555555555555555555555555555555
  
      
        

       

    
#Logout işlemi
@app.route("/logout")
def logout():
    session.clear()
    flash("Başarıyla çıkış yaptınız","success")
    
    return redirect(url_for("index"))


@app.route("/addarticle" , methods = ["GET", "POST"])
def addarticle():
    form = ArticleForm(request.form)
    if request.method == "POST" and form.validate():
        title = form.title.data
        content = form.content.data
        
        cursor = mysql.connection.cursor()
        sorgu = "Insert into articles (title,author,content) VALUES(%s,%s,%s)"
        
        cursor.execute(sorgu,(title,session["username"],content))    
        
        mysql.connection.commit()
        
        cursor.close()
        flash("makale başarıyla eklendi","success")
        return redirect(url_for("dashbord"))
    




    return render_template("addarticle.html", form = form)

#makale sayfası
@app.route("/articles")
def articles():
    cursor = mysql.connection.cursor()
    sorgu = "Select * From articles "
    result = cursor.execute(sorgu)
    if result > 0:
        articles = cursor.fetchall()

        return render_template("articles.html",articles = articles)
    else:
        return render_template("articles.html")

#Detay Sayfası
@app.route("/article/<string:id>")
def article(id):
   cursor=mysql.connection.cursor()
   sorgu = "Select * From articles where id= %s"
   result = cursor.execute(sorgu,(id,))
   if result > 0:
       article = cursor.fetchone()
       return render_template("article.html", article = article)
    
   else:
       return render_template("article.html")

    

    

#makale silme
@app.route("/delete/<string:id>")
@login_required
def delete(id):
    cursor = mysql.connection.cursor()
    sorgu = "Select * from  articles where author = %s and id = %s"

    result = cursor.execute(sorgu,(session["username"],id))
    
    if result > 0:
        flash("Makaleniz başarıyla silindi","success")
        sorgu2 = "Delete from articles where id = %s"
        cursor.execute(sorgu2,(id,))
        mysql.connection.commit()
        return redirect(url_for("dashbord"))


    else:
        flash("Böyle bir makale yok veya bu işleme yetkiniz yok","danger")
        return redirect(url_for("index"))


#Makale Güncelleme 
@app.route("/edit/<string:id>", methods= ["GET","POST"])
@login_required
def update(id):
    if request.method == "GET":
        cursor = mysql.connection.cursor()

        sorgu = "Select * from articles where id = %s and author= %s"
        result = cursor.execute(sorgu,(id,session["username"]))
        
        if result == 0:
            flash("Böyle bir makale yok veya bu işleme yetkiniz yok","danger")
            return redirect(url_for("index"))

        else:  
            article = cursor.fetchone()
            form = ArticleForm()
            form.title.data = article["title"]
            form.content.data = article["content"]
            return render_template("update.html", form = form)
    elif request.method == "POST":
        #POST REQUEST
        form = ArticleForm(request.form)
        newTitle = form.title.data
        newContent = form.content.data

        sorgu2 = "Update articles Set title = %s, content= %s where id= %s"
        cursor=mysql.connection.cursor()
        cursor.execute(sorgu2,(newTitle,newContent,id))
        mysql.connection.commit()
        flash("makale başarıyla güncellendi","success")
        return redirect(url_for("dashbord"))

#arama url
@app.route("/search",methods=["GET","POST"])
def search():
    if request.method == "GET":
        return redirect(url_for("index"))
    else:
        keyword = request.form.get("keyword")
        cursor = mysql.connection.cursor()
        sorgu = f"Select * from articles where title like '%{keyword}%'"
        result = cursor.execute(sorgu)
        if result == 0 : 
            flash("Aranan kelimeye uygun makale bulunamadı","warning")
            return redirect(url_for("articles"))
        else:
            articles = cursor.fetchall()
            return render_template("articles.html", articles = articles)

    

if __name__=="__main__":
    app.run(debug=True)
