-- 2.  Como o faturamento varia mês a mês e o que explica os melhores e piores meses?
SELECT 
	month, 
	SUM(total_spent) AS total_revenue,
	COUNT(transaction_id) AS total_sales,
	ROUND(SUM(total_spent) / COUNT(transaction_id), 2) AS average_ticket,
	ROUND(AVG(quantity), 2) AS units_per_sale
FROM sales
WHERE month IS NOT NULL
GROUP BY month
ORDER BY total_revenue DESC;