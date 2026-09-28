import os
import sqlite3
from datetime import datetime
from pathlib import Path


# ============================================================
# DATABASE PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(
    exist_ok=True
)

DATABASE_PATH = DATA_DIR / "shopbot.db"


# ============================================================
# CONNECTION
# ============================================================

def get_connection():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    # --------------------------------------------------------
    # USERS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            created_at TEXT NOT NULL
        )
    """)


    # --------------------------------------------------------
    # PRODUCTS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            category TEXT NOT NULL,

            price REAL NOT NULL,

            rating REAL DEFAULT 0,

            stock INTEGER DEFAULT 0,

            description TEXT,

            warranty TEXT,

            specifications TEXT,

            image TEXT
        )
    """)


    # --------------------------------------------------------
    # ORDERS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            order_date TEXT NOT NULL,

            status TEXT NOT NULL,

            total_amount REAL NOT NULL,

            shipping_address TEXT,

            payment_method TEXT,

            FOREIGN KEY(user_id)
                REFERENCES users(id)
        )
    """)


    # --------------------------------------------------------
    # ORDER ITEMS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            order_id INTEGER NOT NULL,

            product_id INTEGER NOT NULL,

            quantity INTEGER NOT NULL,

            price REAL NOT NULL,

            FOREIGN KEY(order_id)
                REFERENCES orders(id),

            FOREIGN KEY(product_id)
                REFERENCES products(id)
        )
    """)


    # --------------------------------------------------------
    # CHAT HISTORY
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER,

            order_id INTEGER,

            product_id INTEGER,

            user_message TEXT NOT NULL,

            predicted_intent TEXT,

            confidence REAL,

            bot_response TEXT,

            created_at TEXT NOT NULL,

            FOREIGN KEY(user_id)
                REFERENCES users(id),

            FOREIGN KEY(order_id)
                REFERENCES orders(id),

            FOREIGN KEY(product_id)
                REFERENCES products(id)
        )
    """)


    # --------------------------------------------------------
    # ANALYTICS EVENTS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analytics_events (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER,

            event_type TEXT NOT NULL,

            product_id INTEGER,

            order_id INTEGER,

            metadata TEXT,

            created_at TEXT NOT NULL
        )
    """)


    connection.commit()

    connection.close()


# ============================================================
# USER FUNCTIONS
# ============================================================

def create_user(
    name,
    email
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO users
        (name, email, created_at)

        VALUES (?, ?, ?)
        """,
        (
            name,
            email,
            datetime.now().isoformat()
        )
    )

    connection.commit()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE email = ?
        """,
        (email,)
    )

    user = cursor.fetchone()

    connection.close()

    return dict(user)


# ============================================================
# PRODUCT FUNCTIONS
# ============================================================

def add_product(
    name,
    category,
    price,
    rating,
    stock,
    description,
    warranty,
    specifications,
    image=""
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO products
        (
            name,
            category,
            price,
            rating,
            stock,
            description,
            warranty,
            specifications,
            image
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,

        (
            name,
            category,
            price,
            rating,
            stock,
            description,
            warranty,
            specifications,
            image
        )
    )

    connection.commit()

    product_id = cursor.lastrowid

    connection.close()

    return product_id


def get_products():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM products
        ORDER BY id
        """
    )

    products = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return products


def get_product(
    product_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM products
        WHERE id = ?
        """,
        (product_id,)
    )

    product = cursor.fetchone()

    connection.close()

    if product is None:

        return None

    return dict(product)


# ============================================================
# ORDER FUNCTIONS
# ============================================================

def create_order(
    user_id,
    items,
    shipping_address,
    payment_method
):

    connection = get_connection()

    cursor = connection.cursor()

    total_amount = 0

    # --------------------------------------------------------
    # Calculate total
    # --------------------------------------------------------

    for item in items:

        product = get_product(
            item["product_id"]
        )

        if product is None:

            connection.close()

            raise ValueError(
                f"Product {item['product_id']} "
                "does not exist."
            )

        if product["stock"] < item["quantity"]:

            connection.close()

            raise ValueError(
                f"Insufficient stock for "
                f"{product['name']}."
            )

        total_amount += (
            product["price"]
            * item["quantity"]
        )


    # --------------------------------------------------------
    # Create order
    # --------------------------------------------------------

    cursor.execute(
        """
        INSERT INTO orders
        (
            user_id,
            order_date,
            status,
            total_amount,
            shipping_address,
            payment_method
        )

        VALUES (?, ?, ?, ?, ?, ?)
        """,

        (
            user_id,
            datetime.now().isoformat(),
            "Processing",
            total_amount,
            shipping_address,
            payment_method
        )
    )

    order_id = cursor.lastrowid


    # --------------------------------------------------------
    # Add order items
    # --------------------------------------------------------

    for item in items:

        product = get_product(
            item["product_id"]
        )

        cursor.execute(
            """
            INSERT INTO order_items
            (
                order_id,
                product_id,
                quantity,
                price
            )

            VALUES (?, ?, ?, ?)
            """,

            (
                order_id,
                item["product_id"],
                item["quantity"],
                product["price"]
            )
        )


        # Reduce stock

        cursor.execute(
            """
            UPDATE products

            SET stock = stock - ?

            WHERE id = ?
            """,

            (
                item["quantity"],
                item["product_id"]
            )
        )


    connection.commit()

    connection.close()

    return order_id


def get_orders_for_user(
    user_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM orders

        WHERE user_id = ?

        ORDER BY order_date DESC
        """,
        (user_id,)
    )

    orders = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return orders


def get_order(
    order_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM orders

        WHERE id = ?
        """,
        (order_id,)
    )

    order = cursor.fetchone()

    connection.close()

    if order is None:

        return None

    return dict(order)


def get_order_items(
    order_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT

            oi.*,

            p.name,

            p.category,

            p.description,

            p.warranty,

            p.specifications,

            p.image

        FROM order_items oi

        JOIN products p
            ON oi.product_id = p.id

        WHERE oi.order_id = ?
        """,
        (order_id,)
    )

    items = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return items


# ============================================================
# CHAT HISTORY
# ============================================================

def save_chat_message(

    user_id,

    message,

    intent,

    confidence,

    response,

    order_id=None,

    product_id=None
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO chat_history
        (
            user_id,
            order_id,
            product_id,
            user_message,
            predicted_intent,
            confidence,
            bot_response,
            created_at
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,

        (
            user_id,
            order_id,
            product_id,
            message,
            intent,
            confidence,
            response,
            datetime.now().isoformat()
        )
    )

    connection.commit()

    connection.close()


def get_chat_history(

    user_id,

    order_id=None,

    product_id=None
):

    connection = get_connection()

    cursor = connection.cursor()

    if order_id is not None:

        cursor.execute(
            """
            SELECT *
            FROM chat_history

            WHERE user_id = ?
            AND order_id = ?

            ORDER BY created_at
            """,

            (
                user_id,
                order_id
            )
        )

    elif product_id is not None:

        cursor.execute(
            """
            SELECT *
            FROM chat_history

            WHERE user_id = ?
            AND product_id = ?

            ORDER BY created_at
            """,

            (
                user_id,
                product_id
            )
        )

    else:

        cursor.execute(
            """
            SELECT *
            FROM chat_history

            WHERE user_id = ?

            ORDER BY created_at
            """,

            (user_id,)
        )


    history = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return history


# ============================================================
# ANALYTICS
# ============================================================

def log_event(

    event_type,

    user_id=None,

    product_id=None,

    order_id=None,

    metadata=""
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO analytics_events
        (
            user_id,
            event_type,
            product_id,
            order_id,
            metadata,
            created_at
        )

        VALUES (?, ?, ?, ?, ?, ?)
        """,

        (
            user_id,
            event_type,
            product_id,
            order_id,
            metadata,
            datetime.now().isoformat()
        )
    )

    connection.commit()

    connection.close()


def get_event_counts():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT

            event_type,

            COUNT(*) AS count

        FROM analytics_events

        GROUP BY event_type

        ORDER BY count DESC
        """
    )

    results = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return results


# ============================================================
# INITIALIZE WHEN IMPORTED
# ============================================================

initialize_database()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "Database:"
    )

    print(
        DATABASE_PATH
    )

    print(
        "Database initialized successfully."
    )

    print(
        f"Products: "
        f"{len(get_products())}"
    )