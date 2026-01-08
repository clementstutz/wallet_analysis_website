from flask import jsonify
from flask_sqlalchemy import SQLAlchemy

# from .views import app
# Create database connection object
# db = SQLAlchemy(app)
db = SQLAlchemy()


class AssetsModel(db.Model):
    """CREATE TABLE IF NOT EXISTS Assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        short_name TEXT NOT NULL,
        name TEXT NOT NULL,
        ticker TEXT NOT NULL UNIQUE,  -- Contrainte d'unicité sur le ticker
        broker TEXT,
        currency TEXT NOT NULL
    );
    """
    __tablename__ = "assets"

    id = db.Column(db.Integer, primary_key=True)
    short_name = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    ticker = db.Column(db.String, unique=True, unique=True, nullable=False)
    broker = db.Column(db.String(255))
    currency = db.Column(db.String, nullable=False)

    orders = db.relationship("Order", backref="asset")


class OrderModel(db.Model):
    """CREATE TABLE IF NOT EXISTS Orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        quantity REAL NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY(asset_id) REFERENCES Assets(id),
        UNIQUE(asset_id, date, quantity, price)  -- Contrainte d'unicité de l'ordre
    );
    """
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey("assets.id"))
    date = db.Column(db.Date, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)


class IdxOrdersDate(db.Model):
    """CREATE INDEX IF NOT EXISTS idx_orders_date ON Orders(date);
        -- Créer un index sur la colonne "date" pour améliorer les performances des requêtes basées sur des dates specifiques"""


class IdxOrdersAssetId(db.Model):
    """CREATE INDEX IF NOT EXISTS idx_orders_asset_id ON Orders(asset_id);
        -- Créer un index sur la colonne "asset_id" pour améliorer les performances des requêtes basées sur un asset specifique"""


class DatesModel(db.Model):
    """CREATE TABLE IF NOT EXISTS Dates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL UNIQUE  -- Stocke chaque date une seule fois
    );
    """
    __tablename__ = "dates"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)


class IdxDatesDate(db.Model):
    """CREATE INDEX IF NOT EXISTS idx_dates_date ON Dates(date);
        -- Créer un index sur la colonne "date" pour améliorer les performances des requêtes basées sur des dates specifiques"""


class PriceModel(db.Model):
    """CREATE TABLE IF NOT EXISTS Prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_id INTEGER NOT NULL,
        date_id INTEGER NOT NULL,
        open REAL,
        close REAL,
        open_other_currency REAL,
        close_other_currency REAL,
        FOREIGN KEY(asset_id) REFERENCES Assets(id),
        FOREIGN KEY(date_id) REFERENCES Dates(id),
        UNIQUE(asset_id, date_id)  -- Unicité par actif et date
    );
    """
    __tablename__ = "prices"

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey("assets.id"))
    date_id = db.Column(db.Date, db.ForeignKey("dates.id"))
    open = db.Column(db.Float, nullable=False)
    close = db.Column(db.Float, nullable=False)
    open_other_currency = db.Column(db.Float, nullable=False)
    close_other_currency = db.Column(db.Float, nullable=False)


class CurrencyRatesModel(db.Model):
    """CREATE TABLE IF NOT EXISTS CurrencyRates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        currency_pair TEXT NOT NULL,
        date TEXT NOT NULL,
        open REAL NOT NULL,
        close REAL NOT NULL,
        UNIQUE(currency_pair, date)  -- Contrainte d'unicité des cotation
    );
    """
    __tablename__ = "currency_rates"

    id = db.Column(db.Integer, primary_key=True)
    currency_pair = db.Column(db.String(255), nullable=False)
    date_id = db.Column(db.Date, db.ForeignKey("dates.id"))
    open = db.Column(db.Float, nullable=False)
    close = db.Column(db.Float, nullable=False)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)


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
