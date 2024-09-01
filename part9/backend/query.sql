-- name: create_or_update_batch :one
INSERT INTO batches (
    reference, sku, purchased_quantity, eta
) VALUES (
    $1, $2, $3, $4
) ON CONFLICT (reference)
DO UPDATE SET sku = $2, purchased_quantity = $3, eta = $4
RETURNING *;

-- name: create_or_update_product :one
INSERT INTO products (
    sku, version_number
) VALUES (
    $1, $2
) ON CONFLICT (sku)
DO UPDATE SET version_number = $2
RETURNING *;

-- name: get_product :one
SELECT *
FROM products
WHERE products.sku = $1;

-- name: get_product_by_batchref :one
SELECT products.*
FROM products
JOIN batches ON products.sku = batches.sku
WHERE batches.reference = $1;


-- name: get_batch :many
SELECT *
FROM batches
WHERE sku = $1;

-- name: get_orderlines :many
SELECT order_lines.*
FROM order_lines
JOIN allocations ON order_lines.id = allocations.orderline_id
JOIN batches ON allocations.batch_id = batches.id
WHERE batches.id = $1;


-- name: add_allocation :one
INSERT INTO allocations (
    orderline_id, batch_id
) VALUES (
    $1, $2
) RETURNING *;

-- name: add_order_line :one
INSERT INTO order_lines (
    sku, qty, orderid
) VALUES (
    $1, $2, $3
) RETURNING *;

-- name: clear_order_lines :exec
DELETE FROM order_lines
USING allocations
WHERE order_lines.id = allocations.orderline_id
AND allocations.batch_id = $1;
