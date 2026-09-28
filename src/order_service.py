from datetime import datetime
from src.database import get_connection


# ============================================================
# ORDER STATUS FLOW
# ============================================================

ORDER_STATUSES = [
    "Processing",
    "Confirmed",
    "Shipped",
    "Out for Delivery",
    "Delivered"
]


# ============================================================
# GET CURRENT ORDER
# ============================================================

def get_order_status(order_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, status
        FROM orders
        WHERE id = ?
        """,
        (order_id,)
    )

    order = cursor.fetchone()

    connection.close()

    if order is None:
        return None

    return {
        "order_id": order["id"],
        "status": order["status"]
    }


# ============================================================
# UPDATE STATUS
# ============================================================

def update_order_status(
    order_id,
    new_status
):

    if new_status not in ORDER_STATUSES:

        raise ValueError(
            f"Invalid order status: {new_status}"
        )

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE orders

        SET status = ?

        WHERE id = ?
        """,
        (
            new_status,
            order_id
        )
    )

    connection.commit()

    updated = cursor.rowcount

    connection.close()

    return updated > 0


# ============================================================
# ADVANCE ORDER
# ============================================================

def advance_order(
    order_id
):

    current = get_order_status(
        order_id
    )

    if current is None:

        return None


    current_status = current["status"]


    if current_status == "Delivered":

        return "Delivered"


    current_index = ORDER_STATUSES.index(
        current_status
    )

    next_status = ORDER_STATUSES[
        current_index + 1
    ]


    update_order_status(
        order_id,
        next_status
    )

    return next_status


# ============================================================
# CANCELLATION
# ============================================================

def can_cancel_order(
    order_id
):

    order = get_order_status(
        order_id
    )

    if order is None:

        return False


    return order["status"] in [
        "Processing",
        "Confirmed"
    ]


# ============================================================
# ORDER SUMMARY
# ============================================================

def get_order_summary(
    order_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT

            o.id,
            o.order_date,
            o.status,
            o.total_amount,
            o.shipping_address,
            o.payment_method,

            COUNT(oi.id) AS item_count

        FROM orders o

        LEFT JOIN order_items oi
            ON o.id = oi.order_id

        WHERE o.id = ?

        GROUP BY o.id
        """,
        (order_id,)
    )

    order = cursor.fetchone()

    connection.close()

    if order is None:

        return None

    return dict(order)


# ============================================================
# CANCEL ORDER
# ============================================================

def cancel_order(
    order_id
):

    if not can_cancel_order(
        order_id
    ):

        return False


    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE orders

        SET status = 'Cancelled'

        WHERE id = ?
        """,
        (order_id,)
    )

    connection.commit()

    success = cursor.rowcount > 0

    connection.close()

    return success


# ============================================================
# DEMO STATUS PROGRESSION
# ============================================================

if __name__ == "__main__":

    print(
        "Available order statuses:"
    )

    for status in ORDER_STATUSES:

        print(
            f" - {status}"
        )