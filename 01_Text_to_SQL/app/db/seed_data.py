import logging
from datetime import datetime, timedelta, timezone
import random
from sqlalchemy import text, Engine
from app.db.session import get_db_engine, get_db_type

logger = logging.getLogger("text_to_sql.seed")


def seed_database(engine: Engine = None) -> None:
    """
    Creates and populates the analytical database schema with realistic sample data.
    Ensures idempotency by checking if tables already exist.
    """
    if engine is None:
        engine = get_db_engine()

    db_type = get_db_type()
    logger.info(f"Checking database schema for seeding on {db_type}...")

    with engine.begin() as conn:
        # Check if products table already exists with data
        if db_type == "sqlite":
            check_query = text("SELECT name FROM sqlite_master WHERE type='table' AND name='products';")
        else:
            check_query = text("SELECT table_name FROM information_schema.tables WHERE table_name = 'products';")

        res = conn.execute(check_query).fetchone()
        if res:
            count = conn.execute(text("SELECT COUNT(*) FROM products")).scalar()
            if count and count > 0:
                logger.info(f"Database tables already initialized with {count} products. Skipping seeding.")
                return

        logger.info("Initializing schema tables and seeding dataset...")

        # Drop tables if partial state
        for tbl in ["inventory_logs", "order_items", "orders", "products", "categories", "customers"]:
            conn.execute(text(f"DROP TABLE IF EXISTS {tbl}"))

        # Create Schema
        pk_auto = "INTEGER PRIMARY KEY AUTOINCREMENT" if db_type == "sqlite" else "SERIAL PRIMARY KEY"
        timestamp_type = "TIMESTAMP" if db_type == "postgresql" else "DATETIME"

        conn.execute(text(f"""
            CREATE TABLE customers (
                customer_id {pk_auto},
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                city VARCHAR(50) NOT NULL,
                country VARCHAR(50) NOT NULL,
                signup_date DATE NOT NULL,
                customer_segment VARCHAR(20) NOT NULL
            );
        """))

        conn.execute(text(f"""
            CREATE TABLE categories (
                category_id {pk_auto},
                category_name VARCHAR(50) UNIQUE NOT NULL,
                description TEXT
            );
        """))

        conn.execute(text(f"""
            CREATE TABLE products (
                product_id {pk_auto},
                product_name VARCHAR(100) NOT NULL,
                category_id INTEGER REFERENCES categories(category_id),
                price DECIMAL(10, 2) NOT NULL,
                cost DECIMAL(10, 2) NOT NULL,
                stock_quantity INTEGER NOT NULL,
                reorder_level INTEGER NOT NULL DEFAULT 10
            );
        """))

        conn.execute(text(f"""
            CREATE TABLE orders (
                order_id {pk_auto},
                customer_id INTEGER REFERENCES customers(customer_id),
                order_date {timestamp_type} NOT NULL,
                total_amount DECIMAL(10, 2) NOT NULL,
                order_status VARCHAR(20) NOT NULL,
                shipping_city VARCHAR(50) NOT NULL
            );
        """))

        conn.execute(text(f"""
            CREATE TABLE order_items (
                order_item_id {pk_auto},
                order_id INTEGER REFERENCES orders(order_id),
                product_id INTEGER REFERENCES products(product_id),
                quantity INTEGER NOT NULL,
                unit_price DECIMAL(10, 2) NOT NULL,
                discount DECIMAL(5, 2) DEFAULT 0.00
            );
        """))

        conn.execute(text(f"""
            CREATE TABLE inventory_logs (
                log_id {pk_auto},
                product_id INTEGER REFERENCES products(product_id),
                change_quantity INTEGER NOT NULL,
                reason VARCHAR(50) NOT NULL,
                created_at {timestamp_type} DEFAULT CURRENT_TIMESTAMP
            );
        """))

        # Seed Categories
        categories = [
            ("Electronics", "Gadgets, smartphones, laptops and accessories"),
            ("Audio", "Headphones, speakers, soundbars and microphones"),
            ("Wearables", "Smartwatches, fitness trackers and AR glasses"),
            ("Office", "Ergonomic chairs, desks, monitors and setups"),
            ("Accessories", "Cables, chargers, hubs and backpacks")
        ]
        for name, desc in categories:
            conn.execute(
                text("INSERT INTO categories (category_name, description) VALUES (:name, :desc)"),
                {"name": name, "desc": desc}
            )

        # Seed Products (Including out-of-stock high-revenue items matching README problem statement!)
        products = [
            ("QuantumX Pro Laptop 16-inch", 1, 1899.99, 1200.00, 15, 5),
            ("UltraSound Noise Cancelling Headphones", 2, 299.99, 140.00, 45, 10),
            ("PulseFit Smartwatch Ultra", 3, 349.99, 180.00, 0, 15),  # Out of stock!
            ("ErgoFlex Mesh Desk Chair", 4, 449.99, 210.00, 12, 5),
            ("ThunderBolt 4 Docking Station", 5, 199.99, 90.00, 30, 8),
            ("VisionPad OLED Tablet 12-inch", 1, 999.99, 600.00, 0, 10),  # Out of stock!
            ("AcousticWave Wireless Speaker", 2, 149.99, 65.00, 60, 12),
            ("Titanium Pro Smart Band", 3, 129.99, 50.00, 25, 10),
            ("Standing Desk Electric Dual-Motor", 4, 699.99, 380.00, 8, 4),
            ("MagCharge Wireless Battery Pack", 5, 79.99, 30.00, 0, 20),   # Out of stock!
            ("StudioMaster Condenser Mic", 2, 249.99, 110.00, 18, 6),
            ("4K Curved Gaming Monitor 34-inch", 1, 799.99, 450.00, 10, 5),
            ("Mechanical RGB Keyboard Pro", 4, 159.99, 70.00, 35, 10),
            ("Precision Wireless Mouse", 4, 89.99, 35.00, 50, 15),
            ("VR Motion Headset Gen-3", 1, 1299.99, 800.00, 0, 5),   # Out of stock!
        ]
        for name, cat_id, price, cost, stock, reorder in products:
            conn.execute(
                text("INSERT INTO products (product_name, category_id, price, cost, stock_quantity, reorder_level) "
                     "VALUES (:name, :cat_id, :price, :cost, :stock, :reorder)"),
                {"name": name, "cat_id": cat_id, "price": price, "cost": cost, "stock": stock, "reorder": reorder}
            )

        # Seed Customers
        first_names = ["Alex", "Sarah", "Michael", "Emily", "David", "Jessica", "James", "Amanda", "Robert", "Elena", "Daniel", "Sophia", "Marcus", "Olivia", "Liam"]
        last_names = ["Chen", "Johnson", "Smith", "Taylor", "Miller", "Davis", "Wilson", "Anderson", "Thomas", "Martinez", "Taylor", "White", "Harris", "Martin", "Clark"]
        cities = ["San Francisco", "New York", "Seattle", "Austin", "Chicago", "Boston", "Los Angeles", "Denver", "Toronto", "London"]
        segments = ["VIP", "Enterprise", "Regular", "Regular", "VIP"]

        base_date = datetime.now(timezone.utc) - timedelta(days=365)

        for i in range(1, 26):
            fn = random.choice(first_names)
            ln = random.choice(last_names)
            email = f"{fn.lower()}.{ln.lower()}{i}@example.com"
            city = random.choice(cities)
            country = "USA" if city not in ["Toronto", "London"] else ("Canada" if city == "Toronto" else "UK")
            s_date = (base_date + timedelta(days=random.randint(0, 300))).strftime("%Y-%m-%d")
            seg = random.choice(segments)
            conn.execute(
                text("INSERT INTO customers (first_name, last_name, email, city, country, signup_date, customer_segment) "
                     "VALUES (:fn, :ln, :email, :city, :country, :s_date, :seg)"),
                {"fn": fn, "ln": ln, "email": email, "city": city, "country": country, "s_date": s_date, "seg": seg}
            )

        # Seed Orders & Order Items
        statuses = ["Completed", "Completed", "Completed", "Shipped", "Processing", "Cancelled"]
        
        order_count = 0
        for cust_id in range(1, 26):
            # Give each customer 1 to 5 orders
            num_orders = random.randint(1, 5)
            for _ in range(num_orders):
                order_count += 1
                o_date = (base_date + timedelta(days=random.randint(30, 350))).strftime("%Y-%m-%d %H:%M:%S")
                status = random.choice(statuses)
                shipping_city = random.choice(cities)

                # Insert dummy order first
                conn.execute(
                    text("INSERT INTO orders (customer_id, order_date, total_amount, order_status, shipping_city) "
                         "VALUES (:cust_id, :o_date, 0.00, :status, :city)"),
                    {"cust_id": cust_id, "o_date": o_date, "status": status, "city": shipping_city}
                )

                order_id = order_count
                
                # Create order items
                total_order_amt = 0.0
                num_items = random.randint(1, 4)
                chosen_products = random.sample(range(1, 16), num_items)

                for p_id in chosen_products:
                    # Get product price
                    price_row = conn.execute(text("SELECT price FROM products WHERE product_id = :p_id"), {"p_id": p_id}).fetchone()
                    u_price = float(price_row[0])
                    qty = random.randint(1, 3)
                    disc = random.choice([0.00, 0.00, 0.05, 0.10])
                    item_total = qty * u_price * (1 - disc)
                    total_order_amt += item_total

                    conn.execute(
                        text("INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount) "
                             "VALUES (:o_id, :p_id, :qty, :u_price, :disc)"),
                        {"o_id": order_id, "p_id": p_id, "qty": qty, "u_price": u_price, "disc": disc}
                    )

                # Update total_amount for order
                conn.execute(
                    text("UPDATE orders SET total_amount = :amt WHERE order_id = :o_id"),
                    {"amt": round(total_order_amt, 2), "o_id": order_id}
                )

        # Seed Inventory Logs
        for p_id in range(1, 16):
            conn.execute(
                text("INSERT INTO inventory_logs (product_id, change_quantity, reason) "
                     "VALUES (:p_id, :qty, :reason)"),
                {"p_id": p_id, "qty": random.choice([50, 100, -5, -10]), "reason": random.choice(["Initial Restock", "Supplier Shipment", "Audit Adjustment"])}
            )

        logger.info(f"Database successfully seeded with {order_count} orders across 25 customers.")
