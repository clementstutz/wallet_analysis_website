import datetime
import pandas as pd
import json
from pathlib import Path
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
import yfinance as yf
from .db.models import save_data_to_database
from portfolio_tracking.domain.portfolio_management import Wallet, Asset, Order, rebuild_assets_structure, load_assets_json_file
from portfolio_tracking.domain.data_downloader import HISTORY_FILENAME_SUFIX
from portfolio_tracking.domain.utils import find_asset_by_ticker, write_assets_json_file
from wallet_app.db.models import init_db


HISTORIES_DIR_PATH = Path(__file__).parent / "stocks_histories"
ASSETS_JSONFILE = HISTORIES_DIR_PATH / "assets.json"

app = Flask(__name__)
app.secret_key = "your_secret_key"  #La clé secrète permet de s'assurer que les données stockées dans les cookies ne sont pas altérées par des tiers.

# Config options - Make sure you created a 'config.py' file.
app.config.from_object("config")
# To get one variable, tape app.config['MY_VARIABLE']

# Initialiser la base de données avec l'application Flask
init_db(app)


@app.route('/')
@app.route('/index/')
def index():
    return render_template("index.html")


@app.route('/view_assets/', methods=['GET', 'POST'])
def view_assets():
    list_of_assets = load_assets_json_file(ASSETS_JSONFILE)

    search_result = None
    if request.method == 'POST':
        ticker = request.form['ticker']
        search_result = yf.Ticker(ticker).info

    return render_template('view_assets.html', list_of_assets=list_of_assets, search_result=search_result)


@app.route('/add_asset', methods=['POST'])
def add_asset():
    new_asset = Asset(request.form['short_name'],
                      request.form['name'],
                      request.form['ticker'],
                      request.form['broker'],
                      request.form['currency'])

    order_dates = request.form.getlist('order_date')
    order_quantities = request.form.getlist('order_quantity')
    order_prices = request.form.getlist('order_price')

    # Charger les actifs existants
    list_of_assets = load_assets_json_file(ASSETS_JSONFILE)

    # Mettre à jour ou ajouter l'actif
    already_exist, asset = find_asset_by_ticker(list_of_assets, new_asset)

    # Ajouter les ordres du formulaire
    orders = []
    for date, quantity, price in zip(order_dates, order_quantities, order_prices):
        orders.append(Order(date, float(quantity), float(price)))
    asset.add_orders(orders)

    if not already_exist:
        list_of_assets.add_asset(asset)

    # Sauvegarder les actifs mis à jour
    write_assets_json_file(assets, ASSETS_JSONFILE)

    return redirect(url_for('view_assets'))


@app.route('/dashboard_wallet/')
def dashboard_wallet():
        assets = load_assets_json_file(ASSETS_JSONFILE)
        today = datetime.date.today()
        end_date = today.strftime("%Y-%m-%d")
        save_dir = HISTORIES_DIR_PATH
        filename_sufix = HISTORY_FILENAME_SUFIX
        interval = "1d"
        assets.download_histories(end_date=end_date,
                                  save_dir=save_dir,
                                  filename_sufix=filename_sufix,
                                  interval=interval)

        return render_template("dashboard_wallet.html")


@app.route('/api/wallet/1')
def wallet():
    assets = load_assets_json_file(ASSETS_JSONFILE)
    save_dir = HISTORIES_DIR_PATH
    filename_sufix = HISTORY_FILENAME_SUFIX
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
    assets = load_assets_json_file(ASSETS_JSONFILE)
    save_dir = HISTORIES_DIR_PATH
    filename_sufix = HISTORY_FILENAME_SUFIX
    assets.load_histories(save_dir=save_dir,
                          filename_sufix=filename_sufix)

    wallet = Wallet(assets)
    wallet.calculate_wallet_valuation()

    return jsonify({
      'status': 'ok',
      'wallet': wallet.to_dict(),
    })


@app.route('/api/wallet/share_value')
def wallet_share_value():
    assets = load_assets_json_file(ASSETS_JSONFILE)
    save_dir = HISTORIES_DIR_PATH
    filename_sufix = HISTORY_FILENAME_SUFIX
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
    assets = load_assets_json_file(ASSETS_JSONFILE)
    save_dir = HISTORIES_DIR_PATH
    filename_sufix = HISTORY_FILENAME_SUFIX
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
    assets = load_assets_json_file(ASSETS_JSONFILE)
    save_dir = HISTORIES_DIR_PATH
    filename_sufix = HISTORY_FILENAME_SUFIX
    assets.load_histories(save_dir=save_dir,
                          filename_sufix=filename_sufix)

    wallet = Wallet(assets)
    twrr_cumulated, dates, _ = wallet.get_wallet_TWRR(wallet.dates[0], wallet.dates[-1])

    return jsonify({
      'status': 'ok',
      'dates': dates,
      'twrr_cumulated': twrr_cumulated,
    })


@app.route('/api/stock/')
def stock():
    assets = load_assets_json_file(ASSETS_JSONFILE)
    save_dir = HISTORIES_DIR_PATH
    filename_sufix = HISTORY_FILENAME_SUFIX
    assets.assets[1].load_history(save_dir=save_dir,
                                  filename_sufix=filename_sufix)

    return jsonify({
      'status': 'ok',
      'asset': assets.assets[1].to_dict()
    })


@app.route('/api/wallet/2')
def get_wallet_data():
    start_date = request.args.get('start', default='2020-01-01')
    end_date = request.args.get('end', default='2024-12-31')
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Charger les données depuis une base de données ou un fichier CSV
    # Pour cet exemple, nous utiliserons des données fictives
    data = {
        'dates': pd.date_range(start=start_date, end=end_date).tolist(),
        'share_value': [100 + i for i in range((end_date - start_date).days + 1)],
        'share_value_2': [200 + i for i in range((end_date - start_date).days + 1)],
        'twrr_cumulated': [300 + i for i in range((end_date - start_date).days + 1)]
    }

    response = {
        'status': 'ok',
        'wallet': {
            'dates': data['dates'],
            'share_value': data['share_value'],
            'share_value_2': data['share_value_2'],
            'twrr_cumulated': data['twrr_cumulated']
        }
    }
    return jsonify(response)
