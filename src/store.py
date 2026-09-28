import csv
import os


DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data"
)


def load_csv(filename):
    path = os.path.join(DATA_DIR, filename)

    with open(path, newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def get_products():
    return load_csv("products.csv")


def get_orders():
    return load_csv("orders.csv")


def get_product(product_id):
    products = get_products()

    for product in products:
        if product["product_id"] == product_id:
            return product

    return None


def get_customer_orders(customer_id="C001"):
    orders = get_orders()

    return [
        order
        for order in orders
        if order["customer_id"] == customer_id
    ]


def get_product_order(product_id, customer_id="C001"):
    orders = get_customer_orders(customer_id)

    matching_orders = [
        order
        for order in orders
        if order["product_id"] == product_id
    ]

    return matching_orders[0] if matching_orders else None