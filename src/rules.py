import re


# ============================================================
# HIGH-CONFIDENCE INTENT RULES
# ============================================================

RULES = {

    # --------------------------------------------------------
    # COUPONS
    # --------------------------------------------------------

    "coupon_codes": [
        r"\bcoupon\b",
        r"\bcoupon code\b",
        r"\bpromo code\b",
        r"\bdiscount code\b",
        r"\bvoucher\b",
        r"\bvoucher code\b",
    ],


    # --------------------------------------------------------
    # DISCOUNTS / OFFERS
    # --------------------------------------------------------

    "discounts_offers": [
        r"\bdiscount\b",
        r"\bdiscounts\b",
        r"\boffer\b",
        r"\boffers\b",
        r"\bpromotion\b",
        r"\bpromotions\b",
        r"\bsale\b",
        r"\bdeal\b",
        r"\bdeals\b",
        r"\bprice reduction\b",
    ],


    # --------------------------------------------------------
    # PRODUCT PRICE
    # --------------------------------------------------------

    "product_inquiry": [
        r"\bprice\b",
        r"\bcost\b",
        r"\bhow much\b",
        r"\brate\b",
        r"\brates\b",
        r"\bcharge\b",
    ],


    # --------------------------------------------------------
    # PRODUCT AVAILABILITY
    # --------------------------------------------------------

    "product_availability": [
        r"\bin stock\b",
        r"\bavailable\b",
        r"\bavailability\b",
        r"\bstock\b",
    ],


    # --------------------------------------------------------
    # WARRANTY
    # --------------------------------------------------------

    "product_warranty": [
        r"\bwarranty\b",
        r"\bguarantee\b",
        r"\bcoverage\b",
    ],


    # --------------------------------------------------------
    # SPECIFICATIONS
    # --------------------------------------------------------

    "product_specifications": [
        r"\bspec\b",
        r"\bspecs\b",
        r"\bspecification\b",
        r"\bspecifications\b",
        r"\btechnical details\b",
        r"\bfeatures\b",
    ],


    # --------------------------------------------------------
    # REVIEWS
    # --------------------------------------------------------

    "product_reviews": [
        r"\breview\b",
        r"\breviews\b",
        r"\brating\b",
        r"\bratings\b",
    ],


    # --------------------------------------------------------
    # ORDER TRACKING
    # --------------------------------------------------------

    "order_tracking": [
        r"\btrack\b",
        r"\btracking\b",
        r"\bwhere is my order\b",
        r"\bwhere is my package\b",
        r"\bwhere is my parcel\b",
        r"\bwhere is my shipment\b",
    ],


    # --------------------------------------------------------
    # DELIVERY TIME
    # --------------------------------------------------------

    "delivery_time": [
        r"\bwhen.*arrive\b",
        r"\bwhen.*delivery\b",
        r"\bdelivery time\b",
        r"\bhow long.*delivery\b",
        r"\bexpected delivery\b",
    ],


    # --------------------------------------------------------
    # ORDER STATUS
    # --------------------------------------------------------

    "order_status": [
        r"\border status\b",
        r"\bstatus of my order\b",
    ],


    # --------------------------------------------------------
    # START RETURN
    # --------------------------------------------------------

    "start_return": [
        r"\bi want to return\b",
        r"\bi need to return\b",
        r"\bwant.*return\b",
        r"\bneed.*return\b",
        r"\bstart.*return\b",
        r"\bsend.*back\b",
    ],


    # --------------------------------------------------------
    # RETURN POLICY
    # --------------------------------------------------------

    "return_policy": [
        r"\breturn policy\b",
        r"\brules.*return\b",
        r"\bconditions.*return\b",
        r"\breturn window\b",
        r"\beligible.*return\b",
    ],


    # --------------------------------------------------------
    # RETURN STATUS
    # --------------------------------------------------------

    "return_status": [
        r"\breturn status\b",
        r"\bstatus.*return\b",
        r"\bhas my return\b",
    ],


    # --------------------------------------------------------
    # REFUND STATUS
    # --------------------------------------------------------

    "refund_status": [
        r"\brefund status\b",
        r"\bstatus.*refund\b",
        r"\bwhen.*refund\b",
        r"\bhow long.*refund\b",
        r"\brefund.*received\b",
    ],


    # --------------------------------------------------------
    # REFUND POLICY
    # --------------------------------------------------------

    "refund_policy": [
        r"\brefund policy\b",
        r"\bhow.*refund.*work\b",
        r"\brefund.*rules\b",
    ],


    # --------------------------------------------------------
    # ORDER CANCELLATION
    # --------------------------------------------------------

    "order_cancellation": [
        r"\bcancel.*order\b",
        r"\bi want to cancel\b",
        r"\bcan i cancel\b",
    ],


    # --------------------------------------------------------
    # ORDER MODIFICATION
    # --------------------------------------------------------

    "order_modification": [
        r"\bmodify.*order\b",
        r"\bchange.*order\b",
        r"\bedit.*order\b",
    ],


    # --------------------------------------------------------
    # MISSING ITEM
    # --------------------------------------------------------

    "missing_item": [
        r"\bmissing item\b",
        r"\bitem.*missing\b",
        r"\bmissing.*product\b",
    ],


    # --------------------------------------------------------
    # DAMAGED ITEM
    # --------------------------------------------------------

    "damaged_item": [
        r"\bdamaged\b",
        r"\bdamage\b",
        r"\bbroken\b",
    ],


    # --------------------------------------------------------
    # WRONG ITEM
    # --------------------------------------------------------

    "wrong_item_received": [
        r"\bwrong item\b",
        r"\bwrong product\b",
        r"\bincorrect item\b",
        r"\breceived.*wrong\b",
    ],


    # --------------------------------------------------------
    # ORDER HISTORY
    # --------------------------------------------------------

    "order_history": [
        r"\border history\b",
        r"\bprevious orders\b",
        r"\bold orders\b",
        r"\bearlier orders\b",
        r"\bprevious purchases\b",
    ],


    # --------------------------------------------------------
    # PAYMENT METHODS
    # --------------------------------------------------------

    "payment_methods": [
        r"\bpayment methods\b",
        r"\bpayment options\b",
        r"\bhow can i pay\b",
        r"\bways to pay\b",
    ],


    # --------------------------------------------------------
    # CASH ON DELIVERY
    # --------------------------------------------------------

    "cash_on_delivery": [
        r"\bcash on delivery\b",
        r"\bcod\b",
        r"\bpay on delivery\b",
    ],


    # --------------------------------------------------------
    # SHIPPING COST
    # --------------------------------------------------------

    "shipping_cost": [
        r"\bshipping cost\b",
        r"\bshipping fee\b",
        r"\bdelivery charge\b",
        r"\bdelivery fee\b",
    ],


    # --------------------------------------------------------
    # INTERNATIONAL SHIPPING
    # --------------------------------------------------------

    "international_shipping": [
        r"\binternational shipping\b",
        r"\bship internationally\b",
        r"\boverseas delivery\b",
    ],
}


# ============================================================
# RULE MATCHER
# ============================================================

def rule_based_intent(text):

    text = text.lower().strip()

    for intent, patterns in RULES.items():

        for pattern in patterns:

            if re.search(
                pattern,
                text
            ):

                return {
                    "intent": intent,
                    "confidence": 1.0,
                    "method": "rule",
                }

    return None