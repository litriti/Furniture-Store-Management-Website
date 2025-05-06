from flask import Flask
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary

app = Flask(__name__)
app.secret_key = '^%^&%^(*^^^&&*^(*^^&$%&*&*%^&$&^'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/dbdoan?charset=utf8mb4" % quote('Admin123')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 8
app.config['CART_KEY'] = 'cart'


db = SQLAlchemy(app)
login = LoginManager(app)

cloudinary.config(cloud_name='dw9r0q4hm',
                  api_key='191621737111745',
                  api_secret='6kGK6czLq5GV4a-3F90CTLykH3M')


