-- name: add_batch :one
INSERT INTO batches (
    reference, sku, _purchased_quantity, eta
) VALUES (
    $1, $2, $3, $4
) RETURNING *;

-- name: get_batch :one
SELECT *
FROM batches
WHERE reference = $1;

-- name: all_batches :many
SELECT *
FROM batches;

-- name: add_product :one
INSERT INTO products (
    sku, version_number
) VALUES (
    $1, $2
) RETURNING *;

-- name: get_product :many
SELECT sqlc.embed(products), sqlc.embed(batches)
FROM products
LEFT JOIN batches ON products.sku = batches.sku
WHERE products.sku = $1;

-- name: all_products :many
SELECT sqlc.embed(products), sqlc.embed(batches)
FROM products
LEFT JOIN batches ON products.sku = batches.sku;
