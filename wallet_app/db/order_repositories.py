from datetime import date
from typing import Optional, Iterable

from portfolio_tracking.ports.order_repository import OrderRepository
from .models import OrderModel, db
from sqlalchemy import func


class SqlAlchemyOrderRepository(OrderRepository):

    def add(
        self,
        asset_id: int,
        order_date: date,
        quantity: float,
        price: float,
    ) -> None:
        order = OrderModel(
            asset_id=asset_id,
            date=order_date,
            quantity=quantity,
            price=price,
        )
        db.session.add(order)
        db.session.commit()

    def list_for_asset(
        self,
        asset_id: int,
        start: Optional[date] = None,
        end: Optional[date] = None,
    ) -> Iterable[OrderModel]:

        query = OrderModel.query.filter_by(asset_id=asset_id)

        if start:
            query = query.filter(OrderModel.date >= start)
        if end:
            query = query.filter(OrderModel.date <= end)

        return query.order_by(OrderModel.date).all()
    
    def get_orders_between_dates(self, asset_id, start, end):
        return (
            db.session.query(OrderModel)
            .filter(
                OrderModel.asset_id == asset_id,
                OrderModel.date.between(start, end)
            )
            .all()
        )

    def get_total_quantity(self, asset_id: int) -> float:
        result = (
            db.session.query(func.sum(OrderModel.quantity))
            .filter(OrderModel.asset_id == asset_id)
            .scalar()
        )
        return result or 0.0
