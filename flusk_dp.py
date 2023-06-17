import io
import os
from datetime import datetime, timedelta
from io import BytesIO
import zipfile
import tempfile


from flask import Flask, render_template, url_for, request,send_from_directory,session, redirect, abort, flash, send_file
from flask_sslify import SSLify
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
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx', 'zip', 'pak'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def check_weght_file(file):
#     if len(file.read()) > app.config('MAX_CONTENT_LENGTH'):
#         flash("Файл слишком большой. Рекомендуется отправлять файл до 16 МБ включительно.")

#Создание экземлпяра объекта
app = Flask(__name__)
sslify = SSLify(app)
app.config['SSL_CERTIFICATE'] = '/etc/nginx/ssl/certificate.crt'
app.config['SSL_PRIVATE_KEY'] = '/etc/nginx/ssl/private.key'


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'fjehqjchekcejai4kfjkae'
#app.permanent_session_lifetime = timedelta(minutes=5)
# app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///D:/python_dp/db.sqlite3'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///db.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


menu = ["Авторизация", "Полезная информация", "Обратная связь"]


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
    AES_key = db.Column(db.BLOB, nullable=True)
    AES_vector = db.Column(db.BLOB, nullable=True)

    def __repr__(self):
        return f"<file {self.id}>"

class decipherFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_decipherfile = db.Column(db.String(500))
    decipher_file = db.Column(db.BLOB, nullable=True)
    userID_file = db.Column(db.Integer, db.ForeignKey('profiles.id'))

    def __repr__(self):
        return f"<file {self.id}>"
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
    if request.method == 'POST':
        try:
            user = db.session.query(Users, Profiles).join(Profiles, Users.id == Profiles.user_id).filter(
                request.form['username'] == Profiles.name and request.form['psw'] == Users.psw).first()

            if user and check_password_hash(user[0].psw, request.form['psw']):
                session.permanent = True
                session['userLogged'] = request.form['username']
                return redirect(url_for('profile', username=session['userLogged']))
            else:
                flash("Неверное имя пользователя или пароль", category="error")
        except:
            flash("Данный пользователь не зарегистрирован", category="error")

    elif 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))

    return render_template('login.html', title="Авторизация", menu=menu)


@app.route("/profile/<username>", methods=['GET','POST'])
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    if request.method == 'POST' and 'filename' in request.files:
        file = request.files['filename']
        if request.content_length <= 16 * 1024 * 1024:
            if file and allowed_file(file.filename):
                if request.form['select-box'] == '1':
                    try:
                        file_data = file.stream.read()
                        AES_key = get_random_bytes(16)
                        cipher=AES.new(AES_key, AES.MODE_CBC)
                        AES_vector = cipher.iv
                        cipherfile = cipher.encrypt(pad(file_data, AES.block_size))
                        user_id = db.session.query(Profiles).filter(Profiles.name == f"{session['userLogged']}").first()
                        f = File(name_file=f'encode'+file.filename, file=cipherfile, userID_file=user_id.id, AES_key=AES_key, AES_vector=AES_vector)
                        db.session.add(f)
                        db.session.commit()
                        flash("Файл успешно зашифрован ", category='success')
                    except:
                        db.session.rollback()
                        flash("Ошибка загрузки файла", category='error')
                else:   # Случай когда пользователь собрался подписать файл
                    try:
                        file_dataRSA = file.stream.read()
                        hash_of_file = sha256(file_dataRSA).hexdigest()
                        user_id = db.session.query(Profiles).filter(Profiles.name == f"{session['userLogged']}").first()
                        get_private = user_id.private_key
                        private_list = get_private.split(",")
                        get_private_tuple = tuple(map(int, private_list))
                        encrypt_msg = encrypt(hash_of_file, get_private_tuple)
                        text_encrypt_msg = list(map(str, encrypt_msg))
                        send_encrypt_msg = ', '.join(text_encrypt_msg)


                        AES_keyRSA = get_random_bytes(16)
                        cipherRSA = AES.new(AES_keyRSA, AES.MODE_CBC)
                        AES_vectorRSA = cipherRSA.iv
                        cipherfileRSA = cipherRSA.encrypt(pad(file_dataRSA, AES.block_size))

                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                            zip_file.writestr(f'{file.filename}', cipherfileRSA)
                            zip_file.writestr(f'signature_{username}.txt', send_encrypt_msg.encode('utf-8'))
                            zip_file.writestr("IV.txt", AES_vectorRSA)
                            # zip_file.writestr("hash.txt", hash_of_file)
                        # os.unlink(temp_file.name)
                        zip_data = zip_buffer.getvalue()

                        f = File(name_file=file.filename.split(".")[0] + '.zip', file=zip_data, userID_file=user_id.id,
                                 AES_key=AES_keyRSA, AES_vector=AES_vectorRSA)
                        db.session.add(f)
                        db.session.commit()
                        flash("Файл успешно загружен", category='success')
                    except:
                        db.session.rollback()
                        flash("Ошибка загрузки файла", category='error')
            else:
                flash("Не выбран файл или его расширение не подходит для загрузки", category='error')
        else:
            flash('Файл имеет размер более 16 МБ. Рекомендуется загружать файлы меньшего размера.')

    if request.method == 'POST' and 'defilename' in request.files:
        file = request.files['defilename']
        if not file:
            flash('файл не выбран', category='error')
        if file and allowed_file(file.filename):
            if request.form['select-box2'] == '1':
                try:
                    query=db.session.query(File).filter(file.filename==File.name_file).first()
                    decipherfile=AES.new(query.AES_key, AES.MODE_CBC, query.AES_vector)
                    defile = unpad(decipherfile.decrypt(file.stream.read()),AES.block_size)
                    # hash_decipher_file = sha256(defile).hexdigest()
                    user_id = db.session.query(Profiles).filter(Profiles.name == f"{session['userLogged']}").first()
                    f = decipherFile(name_decipherfile=f'decode' + file.filename, decipher_file=defile, userID_file=user_id.id)
                    db.session.add(f)
                    db.session.commit()
                    flash("Файл успешно загружен", category='success')
                except:
                    flash('Файл не шифровался этим сайтом', category='error')
                    db.session.rollback()
            else:
                query = db.session.query(File).filter(File.name_file == file.filename).first()
                with zipfile.ZipFile(io.BytesIO(file.stream.read()), "r") as zip_data:
                    file_z = zip_data.read(zip_data.filelist[0])
                    sign = zip_data.read(zip_data.filelist[1])
                    vector = zip_data.read(zip_data.filelist[2])
                member = request.form['member']
                get_public = db.session.query(Profiles).filter(Profiles.name == member).first()
                public_list = get_public.public_key.split(",")
                public_tuple = tuple(map(int, public_list))
                str_sign_elem = sign.decode().split(',')
                int_str_sign_elem = [int(element) for element in str_sign_elem]
                get_hash_shifr_file = decrypt(int_str_sign_elem, public_tuple)
                decipherfileRSA = AES.new(query.AES_key, AES.MODE_CBC, vector)
                defileRSA = unpad(decipherfileRSA.decrypt(file_z), AES.block_size)
                hash_of_defile = sha256(defileRSA).hexdigest()
                if get_hash_shifr_file == hash_of_defile:
                    try:
                        user_id = db.session.query(Profiles).filter(Profiles.name == f"{session['userLogged']}").first()
                        f = decipherFile(name_decipherfile=f'decode' + str(zip_data.namelist()[0]), decipher_file=defileRSA, userID_file=user_id.id)
                        db.session.add(f)
                        db.session.commit()
                        flash("Файл успешно расшифрован и вы можете его скачать", category='success')
                    except:
                        flash('В процессе дешефровки документа произошла ошибка', category='error')
                else:
                    flash('В процессе документа оборота файл был изменён!', category='error')
        else:
            flash("Расширение файла не подходит для загрузки", category='error')

    if request.method == 'POST' and 'button1' in request.form:
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


@app.route('/KeyGenResult/<username>', methods=['GET','POST'])
def KeyGenResult(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return render_template('KeyGenResult.html', title=KeyGenResult, username=username)


@app.route('/download')
def download():
    if 'userLogged' not in session:
        abort(401)
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

@app.route('/download', methods=['POST'])
def delete_file():
    file_name = request.form.get('filename')
    file = db.session.query(File).filter(File.name_file == file_name).first()
    try:
        if file:
            db.session.delete(file)
            db.session.commit()
        flash('Файл успешно удалён')
    except:
        flash('Что то пошло не так')
    return redirect(url_for("download"))

@app.route('/downloaddecipherfile', methods=['POST'])
def delete_defile():
    defile_name = request.form.get('defilename')
    file = db.session.query(decipherFile).filter(decipherFile.name_decipherfile == defile_name).first()
    try:
        if file:
            db.session.delete(file)
            db.session.commit()
        flash('Файл успешно удалён')
    except:
        flash('Что то пошло не так')
    return redirect(url_for("downloaddecipher"))


@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html', title="Страница не найдена", menu=menu), 404

@app.errorhandler(401)
def pageNotFound(error):
    return render_template('page401.html', title="Неавторизованный пользователь", menu=menu), 401


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')



