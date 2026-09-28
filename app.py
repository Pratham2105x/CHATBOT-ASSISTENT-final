import streamlit as st

from src.database import (
    get_products,
    get_product,
    create_user,
    create_order,
    get_orders_for_user,
    get_order,
    get_order_items,
    get_chat_history,
    save_chat_message,
    log_event,
)

from src.chatbot import predict_intent

from src.order_service import (
    ORDER_STATUSES,
    advance_order,
    can_cancel_order,
    cancel_order,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ShopBot",
    page_icon="🛍️",
    layout="wide",
)


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "page": "home",
    "selected_product_id": None,
    "selected_order_id": None,
    "cart": [],
    "user_id": None,
    "product_chats": {},
    "order_chats": {},
}

for key, value in defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value


# ============================================================
# USER
# ============================================================

if st.session_state.user_id is None:

    user = create_user(
        name="Demo User",
        email="demo@shopbot.local",
    )

    st.session_state.user_id = user["id"]


USER_ID = st.session_state.user_id


# ============================================================
# PRODUCTS
# ============================================================

products = get_products()


# ============================================================
# NAVIGATION
# ============================================================

def go_home():

    st.session_state.page = "home"

    st.session_state.selected_product_id = None

    st.session_state.selected_order_id = None


def open_product(product_id):

    st.session_state.selected_product_id = product_id

    st.session_state.selected_order_id = None

    st.session_state.page = "product"


    log_event(
        event_type="product_view",
        user_id=USER_ID,
        product_id=product_id,
    )


def open_cart():

    st.session_state.page = "cart"

    st.session_state.selected_product_id = None

    st.session_state.selected_order_id = None


def open_orders():

    st.session_state.page = "orders"

    st.session_state.selected_product_id = None


# ============================================================
# CART
# ============================================================

def add_to_cart(
    product_id,
    quantity
):

    existing = next(
        (
            item
            for item in st.session_state.cart
            if item["product_id"] == product_id
        ),
        None,
    )


    if existing:

        existing["quantity"] += quantity

    else:

        st.session_state.cart.append(
            {
                "product_id": product_id,
                "quantity": quantity,
            }
        )


    log_event(
        event_type="add_to_cart",
        user_id=USER_ID,
        product_id=product_id,
    )


def remove_from_cart(
    product_id
):

    st.session_state.cart = [
        item
        for item in st.session_state.cart
        if item["product_id"] != product_id
    ]


def cart_total():

    total = 0.0


    for item in st.session_state.cart:

        product = get_product(
            item["product_id"]
        )


        if product:

            total += (
                product["price"]
                * item["quantity"]
            )


    return total


# ============================================================
# PRODUCT RESPONSE
# ============================================================

def generate_product_response(
    message,
    product
):

    prediction = predict_intent(
        message
    )

    intent = prediction["intent"]

    confidence = prediction["confidence"]

    text = prediction["normalized_text"]


    # --------------------------------------------------------
    # PRICE
    # --------------------------------------------------------

    if (
        intent == "price_match"
        or "price" in text
        or "cost" in text
        or "how much" in text
        or "rate" in text
    ):

        response = (
            f"The current price of "
            f"**{product['name']}** is "
            f"**₹{product['price']:,.0f}**."
        )

        return response, intent, confidence


    # --------------------------------------------------------
    # WARRANTY
    # --------------------------------------------------------

    if (
        intent == "product_warranty"
        or "warranty" in text
    ):

        response = (
            f"**{product['name']}** comes with "
            f"**{product['warranty']}**."
        )

        return response, intent, confidence


    # --------------------------------------------------------
    # SPECIFICATIONS
    # --------------------------------------------------------

    if (
        intent == "product_specifications"
        or "specification" in text
        or "technical" in text
        or "feature" in text
    ):

        response = (
            f"Here are the specifications for "
            f"**{product['name']}**:\n\n"
            f"{product['specifications']}"
        )

        return response, intent, confidence


    # --------------------------------------------------------
    # AVAILABILITY
    # --------------------------------------------------------

    if (
        intent == "product_availability"
        or "available" in text
        or "availability" in text
        or "in stock" in text
    ):

        if product["stock"] > 0:

            response = (
                f"Yes. **{product['name']}** is "
                f"currently in stock with "
                f"**{product['stock']} units** available."
            )

        else:

            response = (
                f"Sorry, **{product['name']}** is "
                f"currently out of stock."
            )


        return response, intent, confidence


    # --------------------------------------------------------
    # DISCOUNTS
    # --------------------------------------------------------

    if (
        intent == "discounts_offers"
        or "discount" in text
        or "offer" in text
        or "promotion" in text
        or "sale" in text
    ):

        response = (
            f"The current listed price of "
            f"**{product['name']}** is "
            f"**₹{product['price']:,.0f}**. "
            f"Any active promotional discount will "
            f"be reflected during checkout."
        )

        return response, intent, confidence


    # --------------------------------------------------------
    # DESCRIPTION
    # --------------------------------------------------------

    if (
        intent == "product_inquiry"
        or "description" in text
        or "describe" in text
        or "about" in text
    ):

        return (
            product["description"],
            intent,
            confidence
        )


    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    response = (
        f"I can help you with **{product['name']}**. "
        f"You can ask about its price, availability, "
        f"specifications, warranty, discounts, or "
        f"general product information."
    )


    return response, intent, confidence


# ============================================================
# ORDER RESPONSE
# ============================================================

def generate_order_response(
    message,
    order,
    order_items
):

    prediction = predict_intent(
        message
    )

    intent = prediction["intent"]

    confidence = prediction["confidence"]

    text = prediction["normalized_text"]


    order_id = order["id"]

    status = order["status"]


    product_names = [
        item["name"]
        for item in order_items
    ]


    product_text = ", ".join(
        product_names
    )


    # ========================================================
    # DELIVERY TIME
    # ========================================================

    if intent == "delivery_time":

        if status == "Delivered":

            response = (
                f"Order **#{order_id}** has already "
                f"been **delivered**."
            )

        elif status == "Out for Delivery":

            response = (
                f"Order **#{order_id}** is currently "
                f"**out for delivery** and should arrive soon."
            )

        elif status == "Shipped":

            response = (
                f"Order **#{order_id}** has been "
                f"**shipped** and is currently in transit."
            )

        elif status == "Confirmed":

            response = (
                f"Order **#{order_id}** has been confirmed "
                f"and is being prepared for shipment."
            )

        elif status == "Processing":

            response = (
                f"Order **#{order_id}** is still being "
                f"processed and has not shipped yet."
            )

        else:

            response = (
                f"Order **#{order_id}** is currently "
                f"**{status}**."
            )


        return response, intent, confidence


    # ========================================================
    # TRACKING
    # ========================================================

    if intent == "order_tracking":

        if status == "Delivered":

            response = (
                f"Order **#{order_id}** has already "
                f"been delivered."
            )

        elif status == "Out for Delivery":

            response = (
                f"Order **#{order_id}** is currently "
                f"out for delivery."
            )

        elif status == "Shipped":

            response = (
                f"Order **#{order_id}** is shipped "
                f"and currently in transit."
            )

        else:

            response = (
                f"Order **#{order_id}** is currently "
                f"**{status}**."
            )


        return response, intent, confidence


    # ========================================================
    # ORDER STATUS
    # ========================================================

    if (
        intent == "order_status"
        or "status" in text
    ):

        response = (
            f"Order **#{order_id}** is currently "
            f"**{status}**."
        )

        return response, intent, confidence


    # ========================================================
    # ORDER DELAY
    # ========================================================

    if intent == "order_delay":

        if status == "Delivered":

            response = (
                f"Order **#{order_id}** has already "
                f"been delivered."
            )

        else:

            response = (
                f"Order **#{order_id}** is currently "
                f"**{status}**. If the expected delivery "
                f"date has passed, you can report the delay."
            )


        return response, intent, confidence


    # ========================================================
    # RETURN
    # ========================================================

    if intent == "start_return":

        if status == "Delivered":

            response = (
                f"Order **#{order_id}** has been delivered. "
                f"You can request a return for eligible "
                f"items such as **{product_text}**."
            )

        elif status == "Out for Delivery":

            response = (
                f"Order **#{order_id}** is currently out "
                f"for delivery. Once the product is delivered, "
                f"you can request a return if it is eligible."
            )

        else:

            response = (
                f"Order **#{order_id}** has not been delivered "
                f"yet. A return request can normally be started "
                f"after delivery."
            )


        return response, intent, confidence


    # ========================================================
    # RETURN POLICY
    # ========================================================

    if intent == "return_policy":

        response = (
            f"For order **#{order_id}**, eligible products "
            f"can be returned according to the store's "
            f"return policy."
        )

        return response, intent, confidence


    # ========================================================
    # RETURN STATUS
    # ========================================================

    if intent == "return_status":

        response = (
            f"I don't see a separate return request recorded "
            f"for order **#{order_id}**. The current order "
            f"status is **{status}**."
        )

        return response, intent, confidence


    # ========================================================
    # CANCELLATION
    # ========================================================

    if intent == "order_cancellation":

        if can_cancel_order(
            order_id
        ):

            response = (
                f"Order **#{order_id}** is currently "
                f"**{status}** and can still be cancelled."
            )

        else:

            response = (
                f"Order **#{order_id}** is already "
                f"**{status}** and can no longer be cancelled."
            )


        return response, intent, confidence


    # ========================================================
    # MODIFICATION
    # ========================================================

    if intent == "order_modification":

        if status in [
            "Processing",
            "Confirmed",
        ]:

            response = (
                f"Order **#{order_id}** is currently "
                f"**{status}**. It may still be possible "
                f"to modify the order."
            )

        else:

            response = (
                f"Order **#{order_id}** is already "
                f"**{status}**, so modification may no "
                f"longer be possible."
            )


        return response, intent, confidence


    # ========================================================
    # REFUND STATUS
    # ========================================================

    if intent == "refund_status":

        response = (
            f"I don't see a separate refund record for "
            f"order **#{order_id}** yet. If you have already "
            f"returned an item, the refund status can be "
            f"checked once the return is processed."
        )

        return response, intent, confidence


    # ========================================================
    # REFUND POLICY
    # ========================================================

    if intent == "refund_policy":

        response = (
            f"Refunds for order **#{order_id}** are "
            f"processed after the relevant return is "
            f"approved and processed."
        )

        return response, intent, confidence


    # ========================================================
    # MISSING ITEM
    # ========================================================

    if intent == "missing_item":

        response = (
            f"Order **#{order_id}** contains "
            f"**{product_text}**. If one of these items "
            f"is missing from the delivered package, "
            f"you can report it against this order."
        )

        return response, intent, confidence


    # ========================================================
    # DAMAGED ITEM
    # ========================================================

    if intent == "damaged_item":

        response = (
            f"If an item from order **#{order_id}** "
            f"arrived damaged, you can report the affected "
            f"product for further assistance."
        )

        return response, intent, confidence


    # ========================================================
    # WRONG ITEM
    # ========================================================

    if intent == "wrong_item_received":

        response = (
            f"If you received the wrong item in order "
            f"**#{order_id}**, you can report the incorrect "
            f"product for replacement or return."
        )

        return response, intent, confidence


    # ========================================================
    # ORDER CONTENT
    # ========================================================

    if (
        intent == "order_receipt"
        or "what did i order" in text
        or "which product" in text
        or "products in my order" in text
    ):

        response = (
            f"Order **#{order_id}** contains: "
            f"**{product_text}**."
        )

        return response, intent, confidence


    # ========================================================
    # PAYMENT
    # ========================================================

    if (
        intent in [
            "payment_methods",
            "payment_issue",
            "payment_pending",
        ]
        or "payment method" in text
        or "how did i pay" in text
    ):

        response = (
            f"Order **#{order_id}** was placed using "
            f"**{order['payment_method']}**."
        )

        return response, intent, confidence


    # ========================================================
    # TOTAL
    # ========================================================

    if (
        "total" in text
        or "how much did i pay" in text
    ):

        response = (
            f"The total value of order **#{order_id}** "
            f"is **₹{order['total_amount']:,.0f}**."
        )

        return response, intent, confidence


    # ========================================================
    # FALLBACK
    # ========================================================

    response = (
        f"I can help you with order **#{order_id}**. "
        f"You can ask about its status, tracking, "
        f"delivery, cancellation, modification, "
        f"returns, refunds, payment, or products."
    )


    return response, intent, confidence


# ============================================================
# HEADER
# ============================================================

header1, header2, header3, header4 = st.columns(
    [4, 1, 1, 1]
)


with header1:

    st.markdown(
        "# 🛍️ ShopBot"
    )

    st.caption(
        "AI-powered e-commerce assistant"
    )


with header2:

    if st.button(
        "🏠 Shop",
        use_container_width=True
    ):

        go_home()

        st.rerun()


with header3:

    if st.button(
        f"🛒 Cart ({len(st.session_state.cart)})",
        use_container_width=True
    ):

        open_cart()

        st.rerun()


with header4:

    if st.button(
        "📦 Orders",
        use_container_width=True
    ):

        open_orders()

        st.rerun()


st.divider()


# ============================================================
# SHOP
# ============================================================

if st.session_state.page == "home":

    st.title(
        "Explore Products"
    )

    st.write(
        "Select a product to view information and "
        "ask questions before buying."
    )


    categories = sorted(
        set(
            product["category"]
            for product in products
        )
    )


    selected_category = st.selectbox(
        "Category",
        ["All"] + categories
    )


    if selected_category == "All":

        filtered_products = products

    else:

        filtered_products = [
            product
            for product in products
            if product["category"]
            == selected_category
        ]


    columns = st.columns(4)


    for index, product in enumerate(
        filtered_products
    ):

        with columns[index % 4]:

            st.markdown(
                f"""
                <div style="
                    border:1px solid #ddd;
                    border-radius:12px;
                    padding:16px;
                    margin-bottom:10px;
                    min-height:270px;
                ">

                    <div style="
                        height:120px;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        background:#f7f7f7;
                        border-radius:10px;
                        font-size:60px;
                    ">
                        📦
                    </div>

                    <h4>{product['name']}</h4>

                    <p>⭐ {product['rating']}</p>

                    <h3>
                        ₹{product['price']:,.0f}
                    </h3>

                </div>
                """,
                unsafe_allow_html=True
            )


            if st.button(
                "View Product",
                key=f"product_{product['id']}",
                use_container_width=True
            ):

                open_product(
                    product["id"]
                )

                st.rerun()


# ============================================================
# PRODUCT
# ============================================================

elif st.session_state.page == "product":

    product = get_product(
        st.session_state.selected_product_id
    )


    if product is None:

        st.error(
            "Product not found."
        )

        st.stop()


    if st.button(
        "← Back to Shop"
    ):

        go_home()

        st.rerun()


    left, right = st.columns(
        [1, 1.5]
    )


    with left:

        st.markdown(
            """
            <div style="
                height:350px;
                display:flex;
                align-items:center;
                justify-content:center;
                background:#f7f7f7;
                border-radius:15px;
                font-size:120px;
            ">
                📦
            </div>
            """,
            unsafe_allow_html=True
        )


    with right:

        st.caption(
            product["category"]
        )

        st.title(
            product["name"]
        )

        st.subheader(
            f"₹{product['price']:,.0f}"
        )

        st.write(
            f"⭐ {product['rating']} / 5"
        )

        st.write(
            f"**Product ID:** {product['id']}"
        )

        st.write(
            product["description"]
        )

        st.write(
            f"**Stock:** {product['stock']}"
        )

        st.write(
            f"**Warranty:** {product['warranty']}"
        )


        quantity = st.number_input(
            "Quantity",
            min_value=1,
            max_value=max(
                1,
                product["stock"]
            ),
            value=1,
            key=f"quantity_{product['id']}"
        )


        if st.button(
            "🛒 Add to Cart",
            type="primary",
            use_container_width=True
        ):

            add_to_cart(
                product["id"],
                quantity
            )

            st.success(
                "Product added to cart."
            )


    st.divider()


    tab1, tab2, tab3 = st.tabs(
        [
            "Description",
            "Specifications",
            "Warranty"
        ]
    )


    with tab1:

        st.write(
            product["description"]
        )


    with tab2:

        for specification in product[
            "specifications"
        ].split("|"):

            st.write(
                f"• {specification.strip()}"
            )


    with tab3:

        st.write(
            product["warranty"]
        )


    # ========================================================
    # PRODUCT ASSISTANT
    # ========================================================

    st.divider()

    st.subheader(
        "🤖 Product Assistant"
    )

    st.caption(
        "Ask questions about this product before buying."
    )


    chat_key = (
        f"product_{product['id']}"
    )


    if chat_key not in st.session_state.product_chats:

        st.session_state.product_chats[
            chat_key
        ] = []


    for message in st.session_state.product_chats[
        chat_key
    ]:

        with st.chat_message(
            message["role"]
        ):

            st.write(
                message["content"]
            )


    user_message = st.chat_input(
        f"Ask about {product['name']}..."
    )


    if user_message:

        st.session_state.product_chats[
            chat_key
        ].append(
            {
                "role": "user",
                "content": user_message
            }
        )


        response, intent, confidence = (
            generate_product_response(
                user_message,
                product
            )
        )


        st.session_state.product_chats[
            chat_key
        ].append(
            {
                "role": "assistant",
                "content": response
            }
        )


        save_chat_message(
            user_id=USER_ID,
            product_id=product["id"],
            message=user_message,
            intent=intent,
            confidence=confidence,
            response=response
        )


        log_event(
            event_type="product_chat",
            user_id=USER_ID,
            product_id=product["id"]
        )


        st.rerun()


# ============================================================
# CART
# ============================================================

elif st.session_state.page == "cart":

    st.title(
        "🛒 Your Cart"
    )


    if not st.session_state.cart:

        st.info(
            "Your cart is empty."
        )

        if st.button(
            "Continue Shopping"
        ):

            go_home()

            st.rerun()

        st.stop()


    for item in st.session_state.cart:

        product = get_product(
            item["product_id"]
        )


        if product is None:

            continue


        col1, col2, col3, col4 = st.columns(
            [3, 1, 1, 1]
        )


        with col1:

            st.write(
                f"**{product['name']}**"
            )

            st.caption(
                f"Product ID: {product['id']}"
            )


        with col2:

            st.write(
                f"₹{product['price']:,.0f}"
            )


        with col3:

            st.write(
                f"Quantity: {item['quantity']}"
            )


        with col4:

            if st.button(
                "Remove",
                key=f"remove_{product['id']}"
            ):

                remove_from_cart(
                    product["id"]
                )

                st.rerun()


        st.divider()


    st.subheader(
        f"Cart Total: ₹{cart_total():,.0f}"
    )


    col1, col2 = st.columns(2)


    with col1:

        if st.button(
            "← Continue Shopping",
            use_container_width=True
        ):

            go_home()

            st.rerun()


    with col2:

        if st.button(
            "💳 Buy / Checkout",
            type="primary",
            use_container_width=True
        ):

            st.session_state.page = "checkout"

            st.rerun()


# ============================================================
# CHECKOUT
# ============================================================

elif st.session_state.page == "checkout":

    st.title(
        "💳 Checkout"
    )


    if not st.session_state.cart:

        st.warning(
            "Your cart is empty."
        )

        open_cart()

        st.rerun()


    for item in st.session_state.cart:

        product = get_product(
            item["product_id"]
        )

        if product:

            st.write(
                f"**{product['name']}** × "
                f"{item['quantity']} — "
                f"₹{product['price'] * item['quantity']:,.0f}"
            )


    st.divider()


    st.write(
        f"### Total: ₹{cart_total():,.0f}"
    )


    address = st.text_input(
        "Shipping Address",
        placeholder="Enter delivery address"
    )


    payment_method = st.selectbox(
        "Payment Method",
        [
            "UPI",
            "Credit Card",
            "Debit Card",
            "Cash on Delivery"
        ]
    )


    col1, col2 = st.columns(2)


    with col1:

        if st.button(
            "← Back to Cart",
            use_container_width=True
        ):

            open_cart()

            st.rerun()


    with col2:

        if st.button(
            "Place Order",
            type="primary",
            use_container_width=True
        ):

            if not address.strip():

                st.error(
                    "Please enter a shipping address."
                )

                st.stop()


            try:

                order_id = create_order(
                    user_id=USER_ID,
                    items=st.session_state.cart,
                    shipping_address=address,
                    payment_method=payment_method
                )


                log_event(
                    event_type="order_created",
                    user_id=USER_ID,
                    order_id=order_id
                )


                st.session_state.cart = []

                st.session_state.selected_order_id = (
                    order_id
                )

                st.session_state.page = "orders"

                st.rerun()


            except Exception as error:

                st.error(
                    f"Could not create order: {error}"
                )


# ============================================================
# ORDERS
# ============================================================

elif st.session_state.page == "orders":

    st.title(
        "📦 My Orders"
    )


    orders = get_orders_for_user(
        USER_ID
    )


    if not orders:

        st.info(
            "You haven't placed any orders yet."
        )

        st.stop()


    for order in orders:

        items = get_order_items(
            order["id"]
        )


        product_names = ", ".join(
            item["name"]
            for item in items
        )


        col1, col2, col3, col4 = st.columns(
            [1.3, 3, 1.5, 1.5]
        )


        with col1:

            st.write(
                f"**Order #{order['id']}**"
            )


        with col2:

            st.write(
                product_names
            )


        with col3:

            st.write(
                f"₹{order['total_amount']:,.0f}"
            )


        with col4:

            st.write(
                f"**{order['status']}**"
            )


        if st.button(
            "Open Order",
            key=f"open_{order['id']}",
            use_container_width=True
        ):

            st.session_state.selected_order_id = (
                order["id"]
            )

            st.session_state.page = "order_detail"

            st.rerun()


        st.divider()


# ============================================================
# ORDER DETAIL
# ============================================================

elif st.session_state.page == "order_detail":

    order_id = (
        st.session_state.selected_order_id
    )


    order = get_order(
        order_id
    )


    if order is None:

        st.error(
            "Order not found."
        )

        st.stop()


    items = get_order_items(
        order_id
    )


    if st.button(
        "← Back to My Orders"
    ):

        open_orders()

        st.rerun()


    st.title(
        f"Order #{order_id}"
    )


    # ========================================================
    # STATUS
    # ========================================================

    st.subheader(
        "Order Status"
    )


    current_status = order["status"]


    if current_status in ORDER_STATUSES:

        progress = (
            ORDER_STATUSES.index(
                current_status
            ) + 1
        ) / len(ORDER_STATUSES)


        st.progress(
            progress
        )


    st.write(
        f"Current status: **{current_status}**"
    )


    if current_status != "Delivered":

        if st.button(
            "▶ Advance Status"
        ):

            advance_order(
                order_id
            )

            st.rerun()


    else:

        st.success(
            "Order has been delivered."
        )


    # ========================================================
    # ORDER INFORMATION
    # ========================================================

    st.divider()


    c1, c2, c3 = st.columns(3)


    with c1:

        st.metric(
            "Order ID",
            f"#{order_id}"
        )


    with c2:

        st.metric(
            "Total",
            f"₹{order['total_amount']:,.0f}"
        )


    with c3:

        st.metric(
            "Status",
            current_status
        )


    st.write(
        f"**Order Date:** {order['order_date']}"
    )

    st.write(
        f"**Payment:** {order['payment_method']}"
    )

    st.write(
        f"**Address:** {order['shipping_address']}"
    )


    # ========================================================
    # ORDER PRODUCTS
    # ========================================================

    st.divider()

    st.subheader(
        "Products in this order"
    )


    for item in items:

        st.write(
            f"**{item['name']}** "
            f"× {item['quantity']} "
            f" — Product ID: {item['product_id']}"
        )


    # ========================================================
    # CANCELLATION
    # ========================================================

    if can_cancel_order(
        order_id
    ):

        if st.button(
            "Cancel Order"
        ):

            cancel_order(
                order_id
            )

            st.success(
                "Order cancelled."
            )

            st.rerun()


    # ========================================================
    # ORDER ASSISTANT
    # ========================================================

    st.divider()

    st.subheader(
        "🤖 Order Assistant"
    )


    st.info(
        f"Chat context: **Order #{order_id}**"
    )


    entered_order_id = st.text_input(
        "Enter Order ID",
        value=str(order_id),
        key=f"confirm_{order_id}"
    )


    if entered_order_id.strip() != str(order_id):

        st.warning(
            "Enter the correct Order ID to continue."
        )

        st.stop()


    chat_key = (
        f"order_{order_id}"
    )


    if chat_key not in st.session_state.order_chats:

        st.session_state.order_chats[
            chat_key
        ] = []


    for message in st.session_state.order_chats[
        chat_key
    ]:

        with st.chat_message(
            message["role"]
        ):

            st.write(
                message["content"]
            )


    user_message = st.chat_input(
        f"Ask about Order #{order_id}..."
    )


    if user_message:

        st.session_state.order_chats[
            chat_key
        ].append(
            {
                "role": "user",
                "content": user_message
            }
        )


        # Refresh order from database so chatbot
        # always sees the latest status.

        fresh_order = get_order(
            order_id
        )


        response, intent, confidence = (
            generate_order_response(
                user_message,
                fresh_order,
                items
            )
        )


        st.session_state.order_chats[
            chat_key
        ].append(
            {
                "role": "assistant",
                "content": response
            }
        )


        save_chat_message(
            user_id=USER_ID,
            order_id=order_id,
            message=user_message,
            intent=intent,
            confidence=confidence,
            response=response
        )


        log_event(
            event_type="order_chat",
            user_id=USER_ID,
            order_id=order_id
        )


        st.rerun()