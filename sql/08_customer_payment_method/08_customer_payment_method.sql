-- 8. Como os clientes pagam, e a forma de pagamento está ligada ao valor da compra?
-- 8.1 Por método de pagamento:
SELECT
	payment_method,
	SUM(total_spent) AS total_revenue,
	COUNT(transaction_id) AS total_sales,
	ROUND(AVG(total_spent), 2) AS average_ticket
FROM sales
WHERE payment_method <> 'Not Specified'
GROUP BY payment_method
ORDER BY total_revenue DESC;

-- 8.2 Por canal em cada método de pagamento:
SELECT
	location,
	payment_method,
	SUM(total_spent) AS total_revenue,
	COUNT(transaction_id) AS total_sales,
	ROUND(AVG(total_spent), 2) AS average_ticket
FROM sales
WHERE payment_method <> 'Not Specified'
	AND location <> 'Not Specified'
GROUP BY payment_method, location
ORDER BY payment_method, total_revenue DESC;