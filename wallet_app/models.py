from flask import jsonify
from flask_sqlalchemy import SQLAlchemy

# from .views import app
# Create database connection object
# db = SQLAlchemy(app)
db = SQLAlchemy()


class AssetData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_name = db.Column(db.String(255), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)

# Initialiser la base de données avec l'application Flask
def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.drop_all()
        db.create_all()

# Sauvegarder les données dans la base de données
def save_data_to_database(data):
    print('data =\n', data)
    asset_data = AssetData(short_name='short_name', date='date', price=10)
    db.session.merge(asset_data)
    db.session.commit()
    print(f"Les données ont été enregistrées dans la base de données avec succès.")