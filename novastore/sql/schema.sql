-- ============================================================
-- NovaStore – SQL Schema (PostgreSQL)
-- ============================================================

-- CUSTOMERS
CREATE TABLE customers (
    id    SERIAL PRIMARY KEY,
    name  TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
);

-- PRODUCTS
CREATE TABLE products (
    id       SERIAL PRIMARY KEY,
    name     TEXT           NOT NULL,
    price    DECIMAL(10, 2) NOT NULL,
    category TEXT,
    stock    INT            DEFAULT 0
);

-- ORDERS
CREATE TABLE orders (
    id          SERIAL PRIMARY KEY,
    customer_id INT  REFERENCES customers(id),
    status      TEXT NOT NULL DEFAULT 'created',
    created_at  TIMESTAMP DEFAULT NOW()
);

-- ORDER ITEMS
CREATE TABLE order_items (
    id         SERIAL PRIMARY KEY,
    order_id   INT REFERENCES orders(id),
    product_id INT REFERENCES products(id),
    quantity   INT NOT NULL
);

-- INDEX: snabbar upp sök på email (Del 3 + Del 5 Problem A)
CREATE INDEX idx_customers_email ON customers(email);

-- ============================================================
-- Exempeldata – kunder, produkter, en order
-- ============================================================

INSERT INTO customers (name, email) VALUES
    ('Sara',  'sara@example.com'),
    ('Ahmed', 'ahmed@example.com'),
    ('Lisa',  'lisa@example.com');

INSERT INTO products (name, price, category, stock) VALUES
    ('Laptop',      12990.00, 'Elektronik', 5),
    ('Hörlurar',      899.00, 'Elektronik', 20),
    ('Skrivbord',    3499.00, 'Möbler',      3),
    ('Kontorsstol',  2199.00, 'Möbler',     10),
    ('Tangentbord',   599.00, 'Elektronik', 15);

INSERT INTO orders (customer_id, status) VALUES
    (1, 'created'),
    (2, 'shipped'),
    (1, 'delivered');

INSERT INTO order_items (order_id, product_id, quantity) VALUES
    (1, 1, 1),   -- Sara köpte 1 Laptop
    (1, 2, 2),   -- Sara köpte 2 Hörlurar
    (2, 3, 1),   -- Ahmed köpte 1 Skrivbord
    (3, 5, 1);   -- Sara köpte 1 Tangentbord
