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
    reference VARCHAR(255),
    sku VARCHAR(255),
    _purchased_quantity INTEGER NOT NULL,
    eta DATE
);

-- Table: allocations
CREATE TABLE allocations (
    id SERIAL PRIMARY KEY,
    orderline_id INTEGER REFERENCES order_lines(id),
    batch_id INTEGER REFERENCES batches(id)
);
