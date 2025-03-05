from flask import Flask, session
from routes.web import web
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.register_blueprint(web)

if __name__ == '__main__':
    app.run(debug=True)
