CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price INTEGER NOT NULL
);

INSERT INTO products (name, price)
SELECT 'Laptop', 65000
WHERE NOT EXISTS (
    SELECT 1 FROM products WHERE name = 'Laptop'
);

INSERT INTO products (name, price)
SELECT 'Keyboard', 2000
WHERE NOT EXISTS (
    SELECT 1 FROM products WHERE name = 'Keyboard'
);


CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL
);
