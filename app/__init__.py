from flask import Flask
from qrcard.views import qrcard_bp

app = Flask(__name__)
app.config.from_object('app.config')
app.register_blueprint(qrcard_bp)
