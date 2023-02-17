import os
from datetime import datetime


from flask import Flask, render_template, url_for, request
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
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['SECRET_KEY'] = 'supersecretkey'


app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///D:/python_dp/db.sqlite3'
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# class UploadFileForm(FlaskForm):
#     file = FileField("File", validators=[InputRequired()])
#     submit = SubmitField("Upload File")


@app.route('/')
def content():
    crypto_methods = [{'id': 1, 'name_method': 'RSA'},
                      {'id': 2, 'name_method': 'magma'}
                      ]
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    tm = env.get_template('contents.html')
    msg = tm.render(methods_name=crypto_methods, domain='http://192.168.0.103:5000', title="Сайтик для шифрования файлов")
    return msg


@app.route('/RSA', methods=['GET', 'POST'])
def RSA():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #new_filename = f'{filename.split(".")[0]}' + f'{str(datetime.day)}.' + f'{filename.split(".", 1)[1].lower()}'
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'D:/python_dp/Downloads', secure_filename(file.filename)))
        return 'Uploaded'
    return render_template('RSA.html', domain='http://192.168.0.103:5000/RSA', title="RSA")
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
    return render_template('magma.html', domain='http://192.168.0.103:5000/magma', title="magma")





if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')



