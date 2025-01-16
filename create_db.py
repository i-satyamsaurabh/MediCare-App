from app import app
from model import db


with app.app_context():
    db.create_all()