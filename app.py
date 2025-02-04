from flask import Flask
from backend.models import db
from backend.api_controllers import *
app = Flask(__name__, static_folder='static')
app.secret_key = b'8ac11869e7d32a81f9f21317df1e2d70'  

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.sqlite3'  # Database file is quiz.sqlite3
db.init_app(app)  # Connect Flask app to SQLAlchemy
api.init_app(app)  # Connect Flask app to Flask-RESTful
app.app_context().push()  # Allows direct access to DB in other modules
app.debug = True  # Enable debugging mode
print("Quiz app is started")

# Import controllers (routes)
from backend.controllers import *

if __name__ == '__main__':
    app.run()

