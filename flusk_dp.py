import os
from datetime import datetime, timedelta
from io import BytesIO


from flask import Flask, render_template, url_for, request,send_from_directory,session, redirect, abort, flash, send_file
# from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from RSA import Generate_Keypair
# from flask_wtf import FlaskForm
# from wtforms import FileField, SubmitField
from jinja2 import Template, FileSystemLoader, FunctionLoader, Environment
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
# from wtforms.validators import InputRequired


UPLOAD_FOLDER = 'D:/python_dp/Downloads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


#Создание экземлпяра объекта
app = Flask(__name__)


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'fjehqjchekcejai4kfjkae'
#app.permanent_session_lifetime = timedelta(minutes=5)
# app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///D:/python_dp/db.sqlite3'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///db.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)



menu = ["Авторизация", "Полезная информация", "Обратная связь"]


# class UploadFileForm(FlaskForm):
#     file = FileField("File", validators=[InputRequired()])
#     submit = SubmitField("Upload File")

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    psw = db.Column(db.String(500), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<users {self.id}>"

class Profiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    Years = db.Column(db.Integer)
    city = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    public_key = db.Column(db.String)
    private_key = db.Column(db.String)

    def __repr__(self):
        return f"<profiles {self.id}>"

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_file = db.Column(db.String(500))
    file = db.Column(db.BLOB, nullable=True)
    userID_file = db.Column(db.Integer, db.ForeignKey('profiles.id'))

    def __repr__(self):
        return f"<file {self.id}>"

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        try:
            hash_psw = generate_password_hash(request.form['psw'])
            u = Users(email=request.form['email'], psw=hash_psw)
            db.session.add(u)
            db.session.flush()

            p = Profiles(name=request.form['name'], Years=request.form['old'], city=request.form['city'], user_id=u.id)
            db.session.add(p)
            db.session.commit()
            return redirect(url_for('login'))
        except:
            db.session.rollback()
            print("Ошибка добавления в БД")
    return render_template('register.html', title='Регистрация', menu=menu)


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == 'POST' and request.form[
        'username'] == f"{db.session.query(Profiles.name).filter(Profiles.name == request.form['username']).first()[0]}" and check_password_hash(
            db.session.query(Users, Profiles).join(Profiles, Users.id == Profiles.user_id).filter(
                    request.form['username'] == Profiles.name and request.form['psw'] == Users.psw).first()[0].psw,
            request.form['psw']):
        session.permanent = True
        session['userLogged'] = request.form['username']
        return redirect(url_for('profile', username=session['userLogged']))
    elif 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    return render_template('login.html', title="Авторизация", menu=menu)

@app.route("/profile/<username>", methods=['GET','POST'])
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    crypto_methods = [{'id': 1, 'name_method': 'RSA'},
                      {'id': 2, 'name_method': 'magma'}
                      ]
    if request.method == 'POST' and request.form["button"]:
        if not Profiles.query.filter(Profiles.name == f'{username}').first().public_key or not Profiles.query.filter(Profiles.name == f'{username}').first().private_key:
            try:
                private, public = Generate_Keypair()
                pr = Profiles.query.filter(Profiles.name == username).first()
                pb = Profiles.query.filter(Profiles.name == username).first()
                pr.private_key = f'{private[0]},{private[1]}'
                pb.public_key = f'{public[0]},{public[1]}'
                db.session.commit()
                return redirect(url_for('KeyGenResult', username=username))
            except:
                print("Ошибка добавление ключей в базу данных")
                db.session.rollback()
        else:
            flash("Ключи уже сгенерированы", category='error')
    return render_template('profile.html', title=username, username=username, menu=menu, methods_name=crypto_methods)


@app.route('/logout')
def logout():
    session.pop("userLogged", None)
    return redirect(url_for("login"))

@app.route('/RSA', methods=['GET', 'POST'])
def RSA():
    if request.method == 'POST' and request.files['filename']:
        file = request.files['filename']
        if file and allowed_file(file.filename):
            try:
                user_id = db.session.query(Profiles).filter(Profiles.name == f"{session['userLogged']}").first()
                f = File(name_file=file.filename, file=file.read(), userID_file=user_id.id)
                db.session.add(f)
                db.session.commit()
                flash("Файл успешно загружен")
            except:
                db.session.rollback()
                flash("Ошибка загрузки файла")
    else:
        flash("Не выбран файл", category='error')
    return render_template('RSA.html', title="RSA")

@app.route('/KeyGenResult/<username>', methods=['GET','POST'])
def KeyGenResult(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return render_template('KeyGenResult.html', title=KeyGenResult, username=username)
@app.route('/magma')
def magma():
    if request.method == 'POST' and request.form['file']:
            file = request.form['file']
    #     if file and allowed_file(file.filename):
    #         file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'C:/Users/ae.lavrov/python_dp-main/Downloads', secure_filename(file.filename)))
    #     return 'Uploaded'
    # # form = UploadFileForm()
    # # if form.validate_on_submit():
    # #     file = form.file.data
    # #     file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
    # #     return ('File has been uploaded')
    return render_template('magma.html', domain='http://localhost:5000/magma', title="magma", menu=menu)


@app.route('/download')
def download():
    # if 'userLogged' not in session or session['userLogged'] != username:
    #     abort(401)
    username = session['userLogged']
    name_files = []
    upload = db.session.query(File).join(Profiles, Profiles.id == File.userID_file).filter(Profiles.name == f'{username}').all()
    for i in range(len(upload)):
        name_files.append({'name': upload[i].name_file,'id': upload[i].id})
    return render_template('download.html', name_files=name_files)

@app.route('/download/<upload_id>')
def download_file(upload_id):
    upload_file = db.session.query(File).filter(File.id == upload_id).first()
    return  send_file(BytesIO(upload_file.file), download_name = upload_file.name_file, as_attachment=True)

@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html', title="Страница не найдена", menu=menu), 404

@app.errorhandler(401)
def pageNotFound(error):
    return render_template('page401.html', title="Неавторизованный пользователь", menu=menu), 404


# with app.test_request_context():
#     print(url_for('profile'))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')



