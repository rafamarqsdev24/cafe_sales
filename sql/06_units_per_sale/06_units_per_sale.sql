-- 6. Quantas unidades o cliente leva por venda, e o ticket cresce com a quantidade?
SELECT
	quantity,
    COUNT(transaction_id) AS total_sales,
    ROUND(AVG(total_spent), 2) AS average_ticket,
	ROUND(AVG(price_per_unit), 2) AS average_unit_price
FROM sales
GROUP BY quantity
ORDER BY quantity;