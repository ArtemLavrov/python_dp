from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///D:/python_dp/db.sqlite3'
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    date = db.Column(db.Date, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True, host='0.0.0.0')
