from src.database import (
    get_products,
    add_product
)


# ============================================================
# PRODUCT CATALOG
# ============================================================

PRODUCTS = [

    {
        "name": "Nova X1 Smartphone",
        "category": "Smartphones",
        "price": 24999,
        "rating": 4.5,
        "stock": 35,
        "description": (
            "A performance-focused smartphone with a 6.5-inch "
            "AMOLED display, 5G connectivity and a high-capacity battery."
        ),
        "warranty": "1 year manufacturer warranty",
        "specifications": (
            "6.5-inch AMOLED | 120Hz | 8GB RAM | 128GB Storage | "
            "5000mAh Battery | 50MP Camera | 5G"
        ),
        "image": ""
    },

    {
        "name": "Nova X1 Pro Smartphone",
        "category": "Smartphones",
        "price": 32999,
        "rating": 4.7,
        "stock": 22,
        "description": (
            "Premium smartphone featuring a high-refresh-rate AMOLED "
            "display, advanced camera system and fast charging."
        ),
        "warranty": "1 year manufacturer warranty",
        "specifications": (
            "6.7-inch AMOLED | 144Hz | 12GB RAM | 256GB Storage | "
            "5200mAh Battery | 108MP Camera | 5G"
        ),
        "image": ""
    },

    {
        "name": "Pulse Buds Wireless",
        "category": "Audio",
        "price": 2999,
        "rating": 4.3,
        "stock": 60,
        "description": (
            "Wireless earbuds with active noise cancellation, "
            "low-latency mode and compact charging case."
        ),
        "warranty": "1 year manufacturer warranty",
        "specifications": (
            "Bluetooth 5.3 | ANC | 30-hour total battery | "
            "IPX4 | USB-C Charging"
        ),
        "image": ""
    },

    {
        "name": "Pulse Buds Pro",
        "category": "Audio",
        "price": 4999,
        "rating": 4.6,
        "stock": 40,
        "description": (
            "Premium wireless earbuds designed for immersive audio "
            "with adaptive noise cancellation."
        ),
        "warranty": "1 year manufacturer warranty",
        "specifications": (
            "Bluetooth 5.3 | Adaptive ANC | 36-hour battery | "
            "IPX5 | Wireless Charging"
        ),
        "image": ""
    },

    {
        "name": "AeroBook 14",
        "category": "Laptops",
        "price": 64999,
        "rating": 4.5,
        "stock": 18,
        "description": (
            "Lightweight 14-inch laptop designed for productivity, "
            "programming and everyday computing."
        ),
        "warranty": "1 year manufacturer warranty",
        "specifications": (
            "14-inch FHD | Intel Core i5 | 16GB RAM | "
            "512GB SSD | Wi-Fi 6 | Windows 11"
        ),
        "image": ""
    },

    {
        "name": "AeroBook Pro 16",
        "category": "Laptops",
        "price": 89999,
        "rating": 4.7,
        "stock": 12,
        "description": (
            "High-performance 16-inch laptop suitable for development, "
            "creative workloads and demanding applications."
        ),
        "warranty": "1 year manufacturer warranty",
        "specifications": (
            "16-inch 2.5K | Intel Core i7 | 16GB RAM | "
            "1TB SSD | RTX 4050 | Windows 11"
        ),
        "image": ""
    },

    {
        "name": "VisionTab 11",
        "category": "Tablets",
        "price": 21999,
        "rating": 4.4,
        "stock": 25,
        "description": (
            "11-inch tablet suitable for entertainment, studying "
            "and everyday productivity."
        ),
        "warranty": "1 year manufacturer warranty",
        "specifications": (
            "11-inch 2K Display | 8GB RAM | 128GB Storage | "
            "8000mAh Battery | Wi-Fi"
        ),
        "image": ""
    },

    {
        "name": "VisionTab Pro 12",
        "category": "Tablets",
        "price": 34999,
        "rating": 4.6,
        "stock": 16,
        "description": (
            "Premium productivity tablet with a high-resolution "
            "display and stylus support."
        ),
        "warranty": "1 year manufacturer warranty",
        "specifications": (
            "12.4-inch AMOLED | 120Hz | 12GB RAM | "
            "256GB Storage | Stylus Support"
        ),
        "image": ""
    },

    {
        "name": "FitTrack S2",
        "category": "Wearables",
        "price": 3999,
        "rating": 4.2,
        "stock": 50,
        "description": (
            "Smart fitness watch with health tracking, activity "
            "monitoring and notifications."
        ),
        "warranty": "1 year manufacturer warranty",
        "specifications": (
            "1.6-inch AMOLED | Heart Rate | SpO2 | GPS | "
            "7-day Battery | IP68"
        ),
        "image": ""
    },

    {
        "name": "FitTrack Pro",
        "category": "Wearables",
        "price": 6999,
        "rating": 4.5,
        "stock": 32,
        "description": (
            "Advanced fitness smartwatch with GPS, health metrics "
            "and sports tracking."
        ),
        "warranty": "1 year manufacturer warranty",
        "specifications": (
            "1.8-inch AMOLED | GPS | Heart Rate | SpO2 | "
            "14-day Battery | 5ATM"
        ),
        "image": ""
    },

    {
        "name": "PowerCore 20K",
        "category": "Accessories",
        "price": 1999,
        "rating": 4.4,
        "stock": 75,
        "description": (
            "High-capacity portable power bank with fast charging "
            "for smartphones and other USB devices."
        ),
        "warranty": "6 months manufacturer warranty",
        "specifications": (
            "20000mAh | 22.5W Fast Charging | USB-C | "
            "2 USB-A Ports | LED Indicator"
        ),
        "image": ""
    },

    {
        "name": "PowerCore Mini",
        "category": "Accessories",
        "price": 999,
        "rating": 4.1,
        "stock": 90,
        "description": (
            "Compact portable charger designed for everyday travel "
            "and emergency charging."
        ),
        "warranty": "6 months manufacturer warranty",
        "specifications": (
            "10000mAh | 18W Fast Charging | USB-C | "
            "Compact Design"
        ),
        "image": ""
    },

    {
        "name": "KeyPro Mechanical Keyboard",
        "category": "Computer Accessories",
        "price": 4499,
        "rating": 4.6,
        "stock": 28,
        "description": (
            "Mechanical keyboard designed for programming and gaming "
            "with tactile switches and customizable lighting."
        ),
        "warranty": "1 year manufacturer warranty",
        "specifications": (
            "Mechanical Switches | RGB | USB-C | "
            "87 Keys | Windows/macOS Compatible"
        ),
        "image": ""
    },

    {
        "name": "Glide Wireless Mouse",
        "category": "Computer Accessories",
        "price": 1499,
        "rating": 4.3,
        "stock": 55,
        "description": (
            "Ergonomic wireless mouse suitable for office work, "
            "programming and general computing."
        ),
        "warranty": "1 year manufacturer warranty",
        "specifications": (
            "2.4GHz Wireless | 1600 DPI | "
            "6 Buttons | USB Receiver"
        ),
        "image": ""
    },

    {
        "name": "ViewMax 27 Monitor",
        "category": "Monitors",
        "price": 18999,
        "rating": 4.5,
        "stock": 20,
        "description": (
            "27-inch monitor designed for productivity, development "
            "and entertainment."
        ),
        "warranty": "3 year manufacturer warranty",
        "specifications": (
            "27-inch IPS | QHD | 75Hz | 5ms | "
            "HDMI | DisplayPort"
        ),
        "image": ""
    },

    {
        "name": "ViewMax Ultra 32",
        "category": "Monitors",
        "price": 29999,
        "rating": 4.7,
        "stock": 14,
        "description": (
            "Large high-resolution monitor designed for multitasking, "
            "creative work and professional productivity."
        ),
        "warranty": "3 year manufacturer warranty",
        "specifications": (
            "32-inch IPS | 4K UHD | 144Hz | 1ms | "
            "HDMI | DisplayPort | HDR"
        ),
        "image": ""
    },

    {
        "name": "SoundBar Mini",
        "category": "Audio",
        "price": 5999,
        "rating": 4.2,
        "stock": 30,
        "description": (
            "Compact soundbar designed to improve television and "
            "desktop audio."
        ),
        "warranty": "1 year manufacturer warranty",
        "specifications": (
            "2.1 Channel | 120W | Bluetooth 5.2 | "
            "HDMI ARC | Optical"
        ),
        "image": ""
    },

    {
        "name": "CamPro 4K Webcam",
        "category": "Computer Accessories",
        "price": 5499,
        "rating": 4.4,
        "stock": 24,
        "description": (
            "4K webcam designed for video calls, streaming and "
            "online meetings."
        ),
        "warranty": "1 year manufacturer warranty",
        "specifications": (
            "4K Video | 30 FPS | Dual Microphone | "
            "Auto Focus | USB-C"
        ),
        "image": ""
    },

    {
        "name": "GamePad X Wireless",
        "category": "Gaming",
        "price": 3999,
        "rating": 4.5,
        "stock": 36,
        "description": (
            "Wireless gaming controller with low-latency connectivity "
            "and ergonomic controls."
        ),
        "warranty": "1 year manufacturer warranty",
        "specifications": (
            "Bluetooth | 2.4GHz | Dual Vibration | "
            "Rechargeable Battery | PC Compatible"
        ),
        "image": ""
    },

    {
        "name": "StreamMic USB",
        "category": "Audio",
        "price": 6999,
        "rating": 4.6,
        "stock": 20,
        "description": (
            "USB condenser microphone designed for streaming, "
            "podcasting, meetings and content creation."
        ),
        "warranty": "1 year manufacturer warranty",
        "specifications": (
            "USB-C | Cardioid Pattern | 24-bit Audio | "
            "Gain Control | Monitoring Jack"
        ),
        "image": ""
    }
]


# ============================================================
# SEED DATABASE
# ============================================================

def seed_products():

    existing_products = get_products()

    existing_names = {
        product["name"]
        for product in existing_products
    }

    added = 0

    for product in PRODUCTS:

        if product["name"] in existing_names:

            continue

        add_product(
            name=product["name"],
            category=product["category"],
            price=product["price"],
            rating=product["rating"],
            stock=product["stock"],
            description=product["description"],
            warranty=product["warranty"],
            specifications=product["specifications"],
            image=product["image"]
        )

        added += 1

    print("=" * 60)
    print("PRODUCT DATABASE SEEDED")
    print("=" * 60)

    print(
        f"Products added : {added}"
    )

    print(
        f"Total products : "
        f"{len(get_products())}"
    )

    print("=" * 60)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    seed_products()