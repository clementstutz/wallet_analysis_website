from datetime import date
import json
from pathlib import Path
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
import yfinance as yf
from .models import save_data_to_database
from portfolio_tracking.wallet_data import Wallet
from portfolio_tracking.yfinance_interface import FILENAME_SUFIX, Asset, Assets, Order, rebuild_assets_structure
from wallet_app.models import init_db


STOCKS_HISTORIES_DIR = Path(__file__).parent / "stocks_histories"
ASSETS_JSON_FILENAME = "assets.json"

app = Flask(__name__)
app.secret_key = "your_secret_key"  #La clé secrète permet de s'assurer que les données stockées dans les cookies ne sont pas altérées par des tiers.

# Config options - Make sure you created a 'config.py' file.
app.config.from_object("config")
# To get one variable, tape app.config['MY_VARIABLE']

# Initialiser la base de données avec l'application Flask
init_db(app)

def load_assets_json_file() -> Assets:
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
        assets.download_histories(end_date=end_date,
                                  save_dir=save_dir,
                                  filename_sufix=filename_sufix,
                                  interval=interval)

        return render_template("dashboard_wallet.html")


@app.route('/api/wallet/1')
def wallet():
    assets = load_assets_json_file()
    save_dir = STOCKS_HISTORIES_DIR
    filename_sufix = FILENAME_SUFIX
    assets.load_histories(save_dir=save_dir,
                          filename_sufix=filename_sufix)

    wallet = Wallet(assets)
    share_value = wallet.get_wallet_share_value(wallet.dates[0], wallet.dates[-1])
    share_value_2, _ = wallet.get_wallet_share_value_2(wallet.dates[0], wallet.dates[-1])
    twrr_cumulated, dates, _ = wallet.get_wallet_TWRR(wallet.dates[0], wallet.dates[-1])
    
    return jsonify({
      'status': 'ok', 
      'wallet': wallet.to_dict(),
      'share_value': share_value,
      'share_value_2': share_value_2,
      'twrr_cumulated': twrr_cumulated,
    })


@app.route('/api/wallet/valuation')
def wallet_valuation():
    assets = load_assets_json_file()
    save_dir = STOCKS_HISTORIES_DIR
    filename_sufix = FILENAME_SUFIX
    assets.load_histories(save_dir=save_dir,
                          filename_sufix=filename_sufix)

    wallet = Wallet(assets)
    wallet.get_wallet_valuation()

    return jsonify({
      'status': 'ok', 
      'wallet': wallet.to_dict(),
    })


@app.route('/api/wallet/share_value')
def wallet_share_value():
    assets = load_assets_json_file()
    save_dir = STOCKS_HISTORIES_DIR
    filename_sufix = FILENAME_SUFIX
    assets.load_histories(save_dir=save_dir,
                          filename_sufix=filename_sufix)

    wallet = Wallet(assets)
    share_value = wallet.get_wallet_share_value(wallet.dates[0], wallet.dates[-1])

    return jsonify({
      'status': 'ok', 
      'wallet': wallet.to_dict(),
      'share_value': share_value,
    })


@app.route('/api/wallet/share_value_2')
def wallet_share_value_2():
    assets = load_assets_json_file()
    save_dir = STOCKS_HISTORIES_DIR
    filename_sufix = FILENAME_SUFIX
    assets.load_histories(save_dir=save_dir,
                          filename_sufix=filename_sufix)

    wallet = Wallet(assets)
    share_value_2, share_number_2 = wallet.get_wallet_share_value_2(wallet.dates[0], wallet.dates[-1])

    return jsonify({
      'status': 'ok', 
      'wallet': wallet.to_dict(),
      'share_value_2': share_value_2,
      'share_number_2': share_number_2,
    })


@app.route('/api/wallet/TWRR')
def wallet_TWRR():
    assets = load_assets_json_file()
    save_dir = STOCKS_HISTORIES_DIR
    filename_sufix = FILENAME_SUFIX
    assets.load_histories(save_dir=save_dir,
                          filename_sufix=filename_sufix)

    wallet = Wallet(assets)
    start_date = "2020-07-09"
    end_date = wallet.dates[-1]
    twrr_cumulated, dates, _ = wallet.get_wallet_TWRR(wallet.dates[wallet.dates.index(start_date)], wallet.dates[wallet.dates.index(end_date)])

    return jsonify({
      'status': 'ok', 
      'dates': dates,
      'twrr_cumulated': twrr_cumulated,
    })


@app.route('/api/stock/')
def stock():
    assets = load_assets_json_file()
    save_dir = STOCKS_HISTORIES_DIR
    filename_sufix = FILENAME_SUFIX
    assets.assets[0].load_history(save_dir=save_dir,
                                  filename_sufix=filename_sufix)

    return jsonify({
      'status': 'ok', 
      'asset': assets.assets[0].to_dict()
    })


if __name__ == "__main__":
    app.run(debug=True)