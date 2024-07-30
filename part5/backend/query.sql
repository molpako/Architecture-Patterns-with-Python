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
