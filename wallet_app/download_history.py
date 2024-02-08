import csv
from datetime import date
from typing import Dict, List
from pathlib import Path
import yfinance as yf
import numpy_financial as npf
import QuantLib as ql

DEBUG = True
FILENAME_SUFIX = '_history.csv'

#### colect datas ####

class Order:
    def __init__(self, date: str, quantity: float, price: float) -> None:
        self.date = date
        self.quantity = quantity
        self.price = price
    
    def to_dict(self) -> Dict:
        return {
            "date": self.date,
            "quantity": self.quantity,
            "price": self.price
        }

class Asset:
    def __init__(self, short_name: str, name: str, ticker: str, broker: str, devise: str, list_of_orders: List[Order]=None) -> None:
        self.short_name = short_name
        self.name = name
        self.ticker = ticker
        self.broker = broker
        self.devise = devise
        self.orders = [] if list_of_orders is None else list_of_orders
        self.dates = []
        self.closes = []

    def add_orders(self, list_of_orders: List[Order]) -> None:
        self.orders.extend(list_of_orders)
    
    def add_dates(self, list_of_dates: List) -> None:
        self.dates.extend(list_of_dates)
    
    def add_closes(self, list_of_closes: List) -> None:
        self.closes.extend(list_of_closes)

    def to_dict(self) -> Dict:
        return {
            "short_name": self.short_name,
            "name": self.name,
            "ticker": self.ticker,
            "broker": self.broker,
            "devise": self.devise,
            "orders": [order.to_dict() for order in self.orders],
            "dates": self.dates,
            "closes": self.closes
        }

class Assets:
    def __init__(self, list_of_assets: List[Asset]=None) -> None:
        self.assets = [] if list_of_assets is None else list_of_assets
    
    def add_asset(self, asset: Asset) -> None:
        self.assets.append(asset)
    
    def to_dict(self) -> Dict:
        return {
            "assets": [asset.to_dict() for asset in self.assets]
        }

def _normalized_name(name: str) -> str:
    return name.replace(' ', '_')\
        .replace('-', '_')\
        .replace('.', '_')\

def _get_history(asset: Asset, end_date: str, save_dir: Path, filename_sufix: str, interval: str='1d'):
    # TODO : Why not use yf.Ticker("the_ticker").history() ?
    data = yf.download(tickers=asset.ticker,
                       start=asset.orders[0].date,
                       end=end_date,
                       interval=interval)
    
    # Réorganiser le DataFrame
    data.reset_index(inplace=True)

    # Sauvegarder au format CSV
    file_path = save_dir / Path(f"{_normalized_name(asset.short_name)}{filename_sufix}")
    data.to_csv(file_path, float_format="%.4f", index=False)
    print(f'Le fichier CSV a ete telecharge avec succes et enregistre sous {file_path}')
    return data

def download_histories(assets: Assets, end_date: str, save_dir: Path, filename_sufix: str=FILENAME_SUFIX, interval: str='1d'):
    Path.mkdir(save_dir, parents=True, exist_ok=True)
    
    for asset in assets.assets:
        _get_history(asset,
                     end_date,
                     save_dir,
                     filename_sufix,
                     interval)

def download_one_history(asset: Asset, end_date: str, save_dir: Path, filename_sufix: str=FILENAME_SUFIX, interval: str='1d'):
    Path.mkdir(save_dir, parents=True, exist_ok=True)
    
    _get_history(asset,
                 end_date,
                 save_dir,
                 filename_sufix,
                 interval)

def rebuild_assets_structure(assets_data) -> Assets:
    """Recréer les objets à partir des données lues depuis le fichier JSON"""
    # TODO : Ajouter dates et closes ???
    restored_assets = Assets([Asset(
        asset_data["short_name"],
        asset_data["name"],
        asset_data["ticker"],
        asset_data["broker"],
        asset_data["devise"],
        [Order(
            order_data["date"],
            order_data["quantity"],
            order_data["price"]
        ) for order_data in asset_data["orders"]]
    ) for asset_data in assets_data["assets"]])
    return restored_assets

def load_one_history(asset: Asset, save_dir: str, filename_sufix: str=FILENAME_SUFIX) -> Asset:
    dates = []
    close = []
    csv_filename = f"{_normalized_name(asset.short_name)}{filename_sufix}"
    with open(Path(save_dir) / csv_filename, 'r', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)
        # Parcourir les lignes du fichier CSV
        for row in csvreader:
            if not 'null' in row['Close']:
                # row est un dictionnaire où les clés sont les noms de colonnes
                dates.append(row['Date'])
                close.append(float(row['Close']))
            else:
                print(f'ERROR in file: {csv_filename}, row = {row}')
                # TODO: Trouver mieux que ça...
                dates.append(row['Date'])
                close.append(close[-1])
    asset.add_dates(dates)
    asset.add_closes(close)
    return asset

def load_histories(assets: Assets, save_dir: str, filename_sufix: str=FILENAME_SUFIX) -> Assets:
    for asset in assets.assets:
        load_one_history(asset, save_dir, filename_sufix)
    return assets



#### process datas ####

class Wallet:
    def __init__(self, dates: List=None, valuation: List=None, ref_wallet_value: float=100, devise: str="EUR") -> None:
        self.dates = [] if dates is None else dates
        self.valuation = [] if valuation is None else valuation
        self.devise = devise
        self.investment = []
        self.twrr = []
        self.twrr_cumulated = []
        self.share_value = []
        self.share_value_2 = []
        self.share_number_2 = []
    
    def add_dates(self, dates: List) -> None:
        self.dates.extend(dates)
    
    def add_valuation(self, valuation: List) -> None:
        self.valuation.extend(valuation)

    def to_dict(self) -> Dict:
        return {
            "dates": self.dates,
            "valuation": self.valuation,
            "investment": self.investment,
            "twrr": self.twrr,
            "twrr_cumulated": self.twrr_cumulated,
            "devise": self.devise
        }


def get_dates(assets: Assets) -> List:  # OK !
    if not isinstance(assets, Assets):
        print('ERROR: assets must be an instance of Assets class.')
        return 1
    dates_temp = set()
    for asset in assets.assets:
        dates_temp.update(asset.dates)
    return list(sorted(dates_temp))

def _get_close_price_of_a_day(date: str, asset: Asset, wallet: Wallet):  # OK !
    if date in asset.dates:
        date_index = asset.dates.index(date)
        return asset.closes[date_index]
    date_index = wallet.dates.index(date)
    previous_date = wallet.dates[date_index-1]
    previous_date_index = asset.dates.index(previous_date)
    return asset.closes[previous_date_index]

def _get_new_investement(date: str, asset: Asset, actions_count: Dict):  # OK !
    for order in asset.orders:
        # TODO : what if order.date is between two consecutive dates ?
        if date == order.date:
            actions_count[asset.short_name] += order.quantity
            return order.price * order.quantity
    return 0

def _get_wallet_time_weighted_rates_of_return(previous_value, current_value, cash_flow):  # OK ..?
    """
    https://www.investopedia.com/terms/t/time-weightedror.asp
    TWR=[(1+HP1)x(1+HP2)×⋯×(1+HPn)]-1
    where:
    TWR= Time-weighted return
    n= Number of sub-periods
    HP= (End Value-(Initial Value+Cash Flow)) / (Initial Value+Cash Flow)
    HPn= Return for sub-period n
    """
    # if DEBUG : print("_previous_value =", previous_value)
    # if DEBUG : print("_current_value =", current_value)
    # if DEBUG : print("_cash_flow =", cash_flow)
    twrr = (current_value - (previous_value + cash_flow)) / (previous_value + cash_flow)
    # if DEBUG : print("_twrr =", twrr)
    if abs(twrr) < 1.e-10:
        return 0
    return twrr

def get_wallet_valuation(wallet: Wallet, assets: Assets, ref_wallet_value: float=100) -> Wallet:  # OK !
    """Return the wallet with its valorisation over time"""
    if wallet.dates == []:
        print('ERROR: wallet.dates must have been defined. Please call get_dates.')
        return 1
    actions_count = {asset.short_name: 0 for asset in assets.assets}  # Initialisez un dictionnaire pour suivre le nombre d'actions de chaque asset
    wallet.twrr_cumulated.append(ref_wallet_value)
    investement = 0
    for date in wallet.dates:
        total_valuation = 0  # Initialisez la valeur totale du portefeuille à 0
        for asset in assets.assets:
            if asset.dates[0] <= date <= asset.dates[-1]:
                close_price = _get_close_price_of_a_day(date, asset, wallet)
                investement += _get_new_investement(date, asset, actions_count)
                total_valuation += close_price * actions_count[asset.short_name]
            else:
                pass
        
        wallet.valuation.append(total_valuation)
        wallet.investment.append(investement)

        if date != wallet.dates[0]:
            wallet.twrr.append(
                _get_wallet_time_weighted_rates_of_return(
                    wallet.valuation[-2],
                    wallet.valuation[-1],
                    (wallet.investment[-1] - wallet.investment[-2])
                )
            )
            wallet.twrr_cumulated.append(wallet.twrr_cumulated[-1] * (1 + wallet.twrr[-1]))

    return wallet

def _current_share_value(current_wallet_value: float, net_deposit: float, previous_wallet_value: float, previous_share_value: float) -> float:  # OK !
    return (current_wallet_value - net_deposit) / previous_wallet_value * previous_share_value

def get_wallet_share_value(wallet: Wallet, assets: Assets, ref_wallet_value: float=100) -> Wallet:  # OK !
    if not isinstance(wallet, Wallet):
        print('ERROR: wallet must be an instance of Wallet class.')
        return 1
    if wallet.valuation == []:
        print('ERROR: wallet.valuation must have been calculated. Please call get_wallet_valuation.')
        return 1
    
    actions_count = {asset.short_name: 0 for asset in assets.assets}

    wallet.share_value.append(ref_wallet_value)
    current_share_value = wallet.share_value[0]
    for asset in assets.assets:
        _get_new_investement(wallet.dates[0], asset, actions_count)

    for date in wallet.dates[1:]:
        new_value_invested = 0
        for asset in assets.assets:
            if asset.dates[0] <= date <= asset.dates[-1]:
                new_investement = _get_new_investement(date, asset, actions_count)
                new_value_invested += new_investement
            else:
                pass
        current_wallet_value = wallet.valuation[wallet.dates.index(date)]
        net_deposit = new_value_invested
        previous_wallet_value = wallet.valuation[wallet.dates.index(date)-1]
        previous_share_value = current_share_value
        current_share_value = _current_share_value(current_wallet_value, net_deposit, previous_wallet_value, previous_share_value)
        wallet.share_value.append(current_share_value)
    return wallet

def _current_share_value_2(current_wallet_value: float, net_deposit: float, nb_part: float, current_share_value: float) -> float:  # OK !
        if net_deposit == 0:
            return (current_wallet_value) / nb_part, nb_part
        else:
            nb_part = current_wallet_value / current_share_value
            return (current_wallet_value) / nb_part, nb_part

def get_wallet_share_value_2(wallet: Wallet, nb_part: float) -> Wallet:  # OK !
    if not isinstance(wallet, Wallet):
        print('ERROR: wallet must be an instance of Wallet class.')
        return 1
    if wallet.valuation == []:
        print('ERROR: wallet.valuation must have been calculated. Please call get_wallet_valuation.')
        return 1
    
    current_share_value = wallet.valuation[0] / nb_part
    wallet.share_value_2.append(current_share_value)
    wallet.share_number_2.append(nb_part)

    for date in wallet.dates[1:]:
        current_wallet_value = wallet.valuation[wallet.dates.index(date)]
        net_deposit = wallet.investment[wallet.dates.index(date)] - wallet.investment[wallet.dates.index(date)-1]
        current_share_value, nb_part = _current_share_value_2(current_wallet_value, net_deposit, nb_part, current_share_value)
        wallet.share_value_2.append(current_share_value)
        wallet.share_number_2.append(nb_part)
    return wallet



def get_wallet_money_weighted_rates_of_return():
    # TODO : impementer cette fonction
    """
    https://www.investopedia.com/terms/m/money-weighted-return.asp
    PVO=PVI=CF0+CF1/(1+IRR)+CF2/(1+IRR)^2+CF3/(1+IRR)^3+...+CFn/(1+IRR)^n
    where:
    PVO=PV Outflows
    PVI=PV Inflows
    CF0=Initial cash outlay or investment
    CF1,CF2,CF3,...CFn=Cash flows
    N=Each period
    IRR=Initial rate of return
    """
    return 0

def get_wallet_TRI(wallet):
    # TODO : impementer cette fonction
    wallet['TRI'] = []

    return wallet



if __name__ == '__main__':

    order_1 = Order("2024-01-22", 1, 3.75)
    order_2 = Order("2024-02-01", 1, 3.5)
    order_3 = Order("2024-01-22", 1, 28.18)
    

    asset_1 = Asset("Genfit", "Genfit SA", "GNFT.PA", "XTB", "EUR", [order_1])
    asset_1.add_orders([order_2])

    asset_2 = Asset("Spie", "Spie SA", "SPIE.PA", "XTB", "EUR")
    asset_2.add_orders([order_3])

    assets_1 = Assets([asset_1])
    assets_1.add_asset(asset_2)

    assets_2 = Assets()
    assets_2.add_asset(asset_1)
    assets_2.add_asset(asset_2)

    today = date.today()
    end_date = today.strftime("%Y-%m-%d")
    save_dir = Path("")
    filename_sufix = FILENAME_SUFIX
    interval = "1d"
    download_histories(assets=assets_1,
                       end_date=end_date,
                       save_dir=save_dir,
                       filename_sufix=filename_sufix,
                       interval=interval)

    assets_1 = load_histories(assets=assets_1,
                              save_dir=save_dir,
                              filename_sufix=filename_sufix)
    assets_2 = load_histories(assets=assets_2,
                              save_dir=save_dir,
                              filename_sufix=filename_sufix)
    
    dates = get_dates(assets_1)
    if DEBUG : print("dates =\n", dates)

    wallet_1 = Wallet(dates)
    wallet_2 = Wallet(dates)
    if DEBUG : print("wallet_1 =\n", wallet_1)
    if DEBUG : print("wallet_2 =\n", wallet_2)

    if DEBUG : print("wallet_1.dates =\n", wallet_1.dates)
    wallet_1 = get_wallet_valuation(wallet_1,
                                    assets_1)
    if DEBUG : print("wallet_1 =\n", wallet_1.to_dict())
    if DEBUG : print("wallet_1.valuation      = ", wallet_1.valuation)
    if DEBUG : print("wallet_1.twrr_cumulated = ", wallet_1.twrr_cumulated)
    wallet_2 = get_wallet_valuation(wallet_2,
                                    assets_2)

    
    wallet_2 = get_wallet_share_value(wallet=wallet_2,
                                      assets=assets_2)
    if DEBUG : print("wallet_2.valuation      = ", wallet_2.valuation)
    if DEBUG : print("wallet_2.twrr_cumulated = ", wallet_2.twrr_cumulated)
    if DEBUG : print("wallet_2.share_value    = ", wallet_2.share_value)
    
    wallet_2 = get_wallet_share_value_2(wallet=wallet_2,
                                        nb_part=1)
    if DEBUG : print("wallet_2.share_value_2  = ", wallet_2.share_value_2)
    print("assets_2 =\n", assets_2.to_dict())
    print("wallet_2 =\n", wallet_2.to_dict())


    cash_flows = [-100, 50, 40, 30, 20]
    irr = npf.irr(cash_flows)
    print("IRR:", irr)

    dates = [ql.Date(1, 1, 2022), ql.Date(1, 1, 2023), ql.Date(1, 1, 2024)]
    flows = [-100, 50, 40]
    npv = 0
    guess = 0.1
    irr = ql.Irr(flows, npv, guess)
    print("IRR:", irr)