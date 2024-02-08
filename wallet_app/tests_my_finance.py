
from .download_history import Order


def test_orders():
    date = "2024-01-22"
    quantity = 1
    price = 3.75

    order_1 = Order(date, quantity, price)

    order_dic = {
        "date": date,
        "quantity": quantity,
        "price": price
    }
    assert(order_1.date == date)
    assert(order_1.quantity == quantity)
    assert(order_1.price == price)
    assert(order_1.to_dict() == order_dic)


if __name__ == '__main__':
    test_orders()
