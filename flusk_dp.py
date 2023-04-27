import os
from datetime import datetime, timedelta
from io import BytesIO


from flask import Flask, render_template, url_for, request,send_from_directory,session, redirect, abort, flash, send_file
# from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from hashlib import sha256
from RSA import Generate_Keypair, encrypt, decrypt
from Crypto.Cipher import AES
from werkzeug.security import generate_password_hash, check_password_hash
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
# from jinja2 import Template, FileSystemLoader, FunctionLoader, Environment
from werkzeug.utils import secure_filename
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
    AES_key = db.Column(db.Integer)
    AES_vector = db.Column(db.BLOB, nullable=True)

    def __repr__(self):
        return f"<file {self.id}>"

class decipherFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_decipherfile = db.Column(db.String(500))
    decipher_file = db.Column(db.BLOB, nullable=True)
    userID_file = db.Column(db.Integer, db.ForeignKey('profiles.id'))

class HashKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('profiles.user_id'))
    hash_public = db.Column(db.String)
    hash_private = db.Column(db.String)

    def __repr__(self):
        return f"<hash_key {self.id}>"




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
    if request.method == 'POST' and 'filename' in request.files:
        file = request.files['filename']
        if not file:
            flash('файл не выбран', category='error')
        if file and allowed_file(file.filename):
            if not request.form['member']:
                try:
                    AES_key = get_random_bytes(16)
                    cipher=AES.new(AES_key, AES.MODE_CBC)
                    AES_vector = cipher.iv
                    cipherfile = cipher.encrypt(pad(file.stream.read(), AES.block_size))
                    user_id = db.session.query(Profiles).filter(Profiles.name == f"{session['userLogged']}").first()
                    f = File(name_file=f'encode'+file.filename, file=cipherfile, userID_file=user_id.id, AES_key=AES_key, AES_vector=AES_vector)
                    db.session.add(f)
                    db.session.commit()
                    flash("Файл успешно загружен", category='success')
                except:
                    db.session.rollback()
                    flash("Ошибка загрузки файла", category='error')
            else:
                try:
                    member = request.form['member']
                    AES_key = get_random_bytes(16)
                    cipher = AES.new(AES_key, AES.MODE_CBC)
                    AES_vector = cipher.iv
                    cipherfile = cipher.encrypt(pad(file.stream.read(), AES.block_size))
                    user_id = db.session.query(Profiles).filter(Profiles.name == f"{session['userLogged']}").first()
                    #Сделать выборку ключей клиента в чью сторону будет шифроваться
                    hash_cipherfile = sha256(cipherfile).hexdigest()
                    get_private = user_id.private_key
                    private_list = get_private.split(",")
                    get_private_tuple = tuple(private_list)
                    encrypt_msg = encrypt(hash_cipherfile)
                    f = File(name_file=f'encode' + file.filename, file=cipherfile, userID_file=user_id.id,
                             AES_key=AES_key, AES_vector=AES_vector)
                    db.session.add(f)
                    db.session.commit()
                    flash("Файл успешно загружен", category='success')
                except:
                    db.session.rollback()
                    flash("Ошибка загрузки файла", category='error')
        else:
            flash("Не выбран файл или его расширение не подходит для загрузки", category='error')

    if request.method == 'POST' and 'defilename' in request.files:
        file = request.files['defilename']
        if not file:
            flash('файл не выбран', category='error')
        if file and allowed_file(file.filename):
            try:
                filename=file.filename
                query=db.session.query(File).filter(filename==File.name_file).first()
                decipherfile=AES.new(query.AES_key, AES.MODE_CBC, query.AES_vector)
                defile = unpad(decipherfile.decrypt(file.stream.read()),AES.block_size)
                user_id = db.session.query(Profiles).filter(Profiles.name == f"{session['userLogged']}").first()
                f = decipherFile(name_decipherfile=f'decode' + file.filename, decipher_file=defile, userID_file=user_id.id)
                db.session.add(f)
                db.session.commit()
                flash("Файл успешно загружен", category='success')

            except:
                flash('Файл не шифровался этим сайтом')
                db.session.rollback()
        else:
            flash("Не выбран файл или его расширение не подходит для загрузки", category='error')

    if request.method == 'POST' and request.form["button"]:
        if not Profiles.query.filter(Profiles.name == f'{username}').first().public_key or not Profiles.query.filter(Profiles.name == f'{username}').first().private_key:
            try:
                private, public = Generate_Keypair()
                pr = Profiles.query.filter(Profiles.name == username).first()
                pb = Profiles.query.filter(Profiles.name == username).first()
                pr.private_key = f'{private[0]},{private[1]}'
                pb.public_key = f'{public[0]},{public[1]}'
                db.session.commit()
                flash("Ключи успешно сгенерированы")
                # return redirect(url_for('KeyGenResult', username=username))
            except:
                print("Ошибка добавление ключей в базу данных")
                db.session.rollback()
        else:
            flash("Ключи уже сгенерированы", category='info')
    return render_template('profile.html', title=username, username=username, menu=menu)


@app.route('/logout')
def logout():
    session.pop("userLogged", None)
    return redirect(url_for("login"))

# @app.route('/RSA', methods=['GET', 'POST'])
# def RSA():
#     if request.method == 'POST' and request.files['filename']:
#         file = request.files['filename']
#         if file and allowed_file(file.filename):
#             try:
#                 user_id = db.session.query(Profiles).filter(Profiles.name == f"{session['userLogged']}").first()
#                 f = File(name_file=file.filename, file=file.read(), userID_file=user_id.id)
#                 db.session.add(f)
#                 db.session.commit()
#                 flash("Файл успешно загружен")
#             except:
#                 db.session.rollback()
#                 flash("Ошибка загрузки файла")
#     else:
#         flash("Не выбран файл", category='error')
#     return render_template('RSA.html', title="RSA")

@app.route('/KeyGenResult/<username>', methods=['GET','POST'])
def KeyGenResult(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return render_template('KeyGenResult.html', title=KeyGenResult, username=username)


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
    return send_file(BytesIO(upload_file.file), download_name = upload_file.name_file, as_attachment=True)

@app.route('/downloaddecipherfile')
def downloaddecipher():
    # if 'userLogged' not in session or session['userLogged'] != username:
    #     abort(401)
    username = session['userLogged']
    name_defiles = []
    uploaddf = db.session.query(decipherFile).join(Profiles, Profiles.id == decipherFile.userID_file).filter(Profiles.name == f'{username}').all()
    for i in range(len(uploaddf)):
        name_defiles.append({'name': uploaddf[i].name_decipherfile, 'id': uploaddf[i].id})
    return render_template('decrypt.html', name_files=name_defiles)

@app.route('/downloaddecipherfile/<upload_id>')
def downloaddecipherfile_file(upload_id):
    upload_file = db.session.query(decipherFile).filter(decipherFile.id == upload_id).first()
    return send_file(BytesIO(upload_file.decipher_file), download_name=upload_file.name_decipherfile, as_attachment=True)


@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html', title="Страница не найдена", menu=menu), 404

@app.errorhandler(401)
def pageNotFound(error):
    return render_template('page401.html', title="Неавторизованный пользователь", menu=menu), 404


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')



