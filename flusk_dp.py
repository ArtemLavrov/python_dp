import os
from datetime import datetime


from flask import Flask, render_template, url_for, request,send_from_directory,session, redirect,abort
from flask_sqlalchemy import SQLAlchemy
# from flask_wtf import FlaskForm
# from wtforms import FileField, SubmitField
from jinja2 import Template, FileSystemLoader, FunctionLoader, Environment
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
# from wtforms.validators import InputRequired


UPLOAD_FOLDER = 'D:/python_dp/Downloads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


#Создание экземлпяра объекта
app = Flask(__name__)


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'fjehqjchekcejai4kfjkae'


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

    def __repr__(self):
        return f"<profiles {self.id}>"


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
         except:
             db.session.rollback()
             print("Ошибка добавления в БД")

    return render_template('register.html', title='Регистрация', menu=menu)


@app.route("/profile/<username>")
def profile(username):
    if 'userLogged' not in session or session['userLogged']!=username:
        abort(401)
    return render_template('profile.html', title=username, username=username, menu=menu)

@app.route("/login", methods=["POST", "GET"])
def login():
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST' and request.form['username'] == f"{db.session.query(Profiles.name).filter(Profiles.name==request.form['username']).first()[0]}" and check_password_hash(db.session.query(Users,Profiles).join(Profiles,Users.id==Profiles.user_id).filter(request.form['username']==Profiles.name and request.form['psw']==Users.psw).first()[0].psw, request.form['psw']):
        session['userLogged'] = request.form['username']
        return redirect(url_for('profile', username=session['userLogged']))
    return render_template('login.html', title="Авторизация", menu=menu)

@app.route('/')
def content():
    crypto_methods = [{'id': 1, 'name_method': 'RSA'},
                      {'id': 2, 'name_method': 'magma'}
                      ]

    return render_template('contents.html', methods_name=crypto_methods, menu=menu, domain='http://localhost:5000', title="Сайтик для шифрования файлов")
    #file_loader = FileSystemLoader('templates')
    #env = Environment(loader=file_loader)
    # tm = env.get_template('contents.html')
    # msg = tm.render(methods_name=crypto_methods, domain='http://localhost:5000:5000', title="Сайтик для шифрования файлов")
    # return msg


@app.route('/RSA', methods=['GET', 'POST'])
def RSA():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #new_filename = f'{filename.split(".")[0]}' + f'{str(datetime.day)}.' + f'{filename.split(".", 1)[1].lower()}'
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'D:/python_dp/Downloads', secure_filename(file.filename)))
        return 'Uploaded'
    return render_template('RSA.html', domain='http://localhost:5000/RSA', title="RSA", menu=menu)
    # return render_template('RSA.html', domain='http://192.168.0.103:5000/RSA', title = "RSA", form=form)


@app.route('/magma')
def magma():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'D:/python_dp/Downloads', secure_filename(file.filename)))
        return 'Uploaded'
    # form = UploadFileForm()
    # if form.validate_on_submit():
    #     file = form.file.data
    #     file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
    #     return ('File has been uploaded')
    return render_template('magma.html', domain='http://localhost:5000/magma', title="magma", menu=menu)


@app.route('/download')
def download():
    return render_template('download.html', files=os.listdir('D:/python_dp/output'))
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory('D:/python_dp/output', filename)

@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html', title="Страница не найдена", menu=menu), 404



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')



