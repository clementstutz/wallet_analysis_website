from portfolio_tracking.ports.price_repository import PriceRepository
from .models import PriceModel, db

class SqlAlchemyPriceRepository(PriceRepository):

    def get_prices_between_dates(self, asset_id, start, end):
        rows = (
            db.session.query(PriceModel.date, PriceModel.close)
            .filter(
                PriceModel.asset_id == asset_id,
                PriceModel.date.between(start, end)
            )
            .order_by(PriceModel.date)
            .all()
        )
        return rows
