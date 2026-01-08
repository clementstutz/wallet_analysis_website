from portfolio_tracking.ports.asset_repository import AssetRepository
from .models import AssetsModel, db

class SqlAlchemyPriceRepository(AssetRepository):

    def get_all_assets(self):
        raise NotImplementedError

    def get_asset_by_id(self, asset_id):
        raise NotImplementedError
