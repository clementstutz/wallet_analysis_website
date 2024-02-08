from datetime import date
import json
from pathlib import Path
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
import requests
import yfinance as yf
from .models import save_data_to_database
from .download_history import FILENAME_SUFIX, Asset, Assets, Order, Wallet, download_histories, get_dates, get_wallet_valuation, load_histories, load_one_history, rebuild_assets_structure
from wallet_app.models import init_db


METEO_API_KEY = "a228411bf5cf1f6ff4a80b45e9b5b065"  # clé OPENWEATHERMAP
if METEO_API_KEY is None:  # URL de test :
    METEO_API_URL = "https://samples.openweathermap.org/data/2.5/forecast?lat=0&lon=0&appid=xxx"
else:  # URL avec clé :
    METEO_API_URL = "https://api.openweathermap.org/data/2.5/forecast?lat=48.883587&lon=2.333779&appid=" + METEO_API_KEY

STOCKS_HISTORIES_DIR = Path(__file__).parent / "stocks_histories"
ASSETS_JSON_FILENAME = "assets.json"

app = Flask(__name__)
app.secret_key = "your_secret_key"  #La clé secrète permet de s'assurer que les données stockées dans les cookies ne sont pas altérées par des tiers.

# Config options - Make sure you created a 'config.py' file.
app.config.from_object("config")
# To get one variable, tape app.config['MY_VARIABLE']

# Initialiser la base de données avec l'application Flask
init_db(app)

def load_assets_json_file():
    """Charge les actifs depuis le fichier JSON
    et reconstruit l'arboressence en respectant les classes de chaque objet"""
    assets_jsonfile = STOCKS_HISTORIES_DIR / ASSETS_JSON_FILENAME
    with open(assets_jsonfile, 'r', encoding='utf-8') as asset_file:
        assets_data = json.load(asset_file)

    return rebuild_assets_structure(assets_data)


def write_assets_json_file(assets):
    assets_jsonfile = STOCKS_HISTORIES_DIR / ASSETS_JSON_FILENAME
    with open(assets_jsonfile, 'w', encoding='utf-8') as asset_file:
        json.dump(assets.to_dict(), asset_file, indent=4)


def find_asset_by_ticker(assets: Assets, new_asset: Asset):
    """Rechercher un actif dans assets avec son ticker"""
    for asset in assets.assets:
        if asset.ticker == new_asset.ticker:
            return True, asset
    return False, new_asset


@app.route('/')
@app.route('/index/')
def index():
    return render_template("index.html")


@app.route('/view_assets/', methods=['GET', 'POST'])
def view_assets():
    assets = load_assets_json_file()
    
    search_result = None
    if request.method == 'POST':
        ticker = request.form['ticker']
        search_result = yf.Ticker(ticker).info

    return render_template('view_assets.html', assets=assets, search_result=search_result)


@app.route('/add_asset', methods=['POST'])
def add_asset():
    new_asset = Asset(request.form['short_name'],
                      request.form['name'],
                      request.form['ticker'],
                      request.form['broker'],
                      request.form['devise'])

    order_dates = request.form.getlist('order_date')
    order_quantities = request.form.getlist('order_quantity')
    order_prices = request.form.getlist('order_price')

    # Charger les actifs existants
    assets = load_assets_json_file()

    # Mettre à jour ou ajouter l'actif
    already_exist, asset = find_asset_by_ticker(assets, new_asset)
    
    # Ajouter les ordres du formulaire
    orders = []
    for date, quantity, price in zip(order_dates, order_quantities, order_prices):
        orders.append(Order(date, float(quantity), float(price)))
    asset.add_orders(orders)
    
    if not already_exist:
        assets.add_asset(asset)

    # Sauvegarder les actifs mis à jour
    write_assets_json_file(assets)

    return redirect(url_for('view_assets'))


@app.route('/dashboard_wallet/')
def dashboard_wallet():
        assets = load_assets_json_file()
        today = date.today()
        end_date = today.strftime("%Y-%m-%d")
        save_dir = STOCKS_HISTORIES_DIR
        filename_sufix = FILENAME_SUFIX
        interval = "1d"
        download_histories(assets=assets,
                           end_date=end_date,
                           save_dir=save_dir,
                           filename_sufix=filename_sufix,
                           interval=interval)

        return render_template("dashboard_wallet.html")


@app.route('/api/wallet/')
def wallet():
    assets = load_assets_json_file()
    save_dir = STOCKS_HISTORIES_DIR
    filename_sufix = FILENAME_SUFIX
    loaded_data = load_histories(assets=assets,
                                 save_dir=save_dir,
                                 filename_sufix=filename_sufix)

    dates = get_dates(loaded_data)
    wallet1 = Wallet(dates)
    wallet2 = get_wallet_valuation(wallet1, loaded_data)
    
    return jsonify({
      'status': 'ok', 
      'data': wallet2.to_dict()
    })

@app.route('/api/stock/')
def stock():
    assets = load_assets_json_file()
    save_dir = STOCKS_HISTORIES_DIR
    filename_sufix = FILENAME_SUFIX
    loaded_data = load_one_history(asset=assets.assets[0],
                                   save_dir=save_dir,
                                   filename_sufix=filename_sufix)

    return jsonify({
      'status': 'ok', 
      'data': loaded_data.to_dict()
    })






# @app.route('/dashboard_meteo/')
# def dashboard_meteo():
#         return render_template("dashboard_meteo.html")


# @app.route('/api/meteo/')
# def meteo():
#     response = requests.get(METEO_API_URL)
#     content = json.loads(response.content.decode('utf-8'))

#     if response.status_code != 200:
#         return jsonify({
#             'status': 'error',
#             'message': 'La requête à l\'API météo n\'a pas fonctionné. Voici le message renvoyé par l\'API : {}'.format(content['message'])
#         }), 500
    
#     data = [] # On initialise une liste vide
#     for prev in content["list"]:
#         datetime = prev['dt'] * 1000
#         temperature = prev['main']['temp'] - 273.15 # Conversion de Kelvin en °c
#         temperature = round(temperature, 2)
#         data.append([datetime, temperature])
    
#     return jsonify({
#       'status': 'ok', 
#       'data': data
#     })


if __name__ == "__main__":
    app.run(debug=True)