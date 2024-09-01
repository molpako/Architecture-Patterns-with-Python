-- Table: products
CREATE TABLE products (
    sku VARCHAR(255) PRIMARY KEY,
    version_number INTEGER NOT NULL
);

-- Table: order_lines
CREATE TABLE order_lines (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(255),
    qty INTEGER NOT NULL,
    orderid VARCHAR(255)
);

-- Table: batches
CREATE TABLE batches (
    id SERIAL PRIMARY KEY,
    reference VARCHAR(255) UNIQUE,
    sku VARCHAR(255) NOT NULL REFERENCES products(sku),
    purchased_quantity INTEGER NOT NULL,
    eta DATE
);

-- Table: allocations
CREATE TABLE allocations (
    id SERIAL PRIMARY KEY,
    orderline_id INTEGER REFERENCES order_lines(id) ON DELETE CASCADE,
    batch_id INTEGER REFERENCES batches(id) ON DELETE CASCADE
);
