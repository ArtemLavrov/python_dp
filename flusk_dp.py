import os
from datetime import datetime


from flask import Flask, render_template, url_for, request,send_from_directory,session, redirect,abort
from flask_sqlalchemy import SQLAlchemy
# from flask_wtf import FlaskForm
# from wtforms import FileField, SubmitField
from jinja2 import Template, FileSystemLoader, FunctionLoader, Environment
from werkzeug.utils import secure_filename
# from wtforms.validators import InputRequired


UPLOAD_FOLDER = 'D:/python_dp/Downloads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


#Создание экземлпяра объекта
app = Flask(__name__)
menu = ["Авторизация", "Полезная информация", "Обратная связь"]
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'fjehqjchekcejai4kfjkae'


# app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///D:/python_dp/db.sqlite3'
# # app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# db = SQLAlchemy(app)


# class UploadFileForm(FlaskForm):
#     file = FileField("File", validators=[InputRequired()])
#     submit = SubmitField("Upload File")

@app.route("/profile/<username>")
def profile(username):
    if 'userLogged' not in session or session['userLogged']!=username:
        abort(401)
    return render_template('profile.html', title=username, username=username, menu=menu)

@app.route("/login", methods=["POST", "GET"])
def login():
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST' and request.form['username'] == "Artem" and request.form['psw'] == "1234":
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



