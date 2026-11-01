-- 1.  Qual foi o desempenho geral de 2023?
-- 1.1 Por ano:
SELECT 
	2023 AS year,
	SUM(total_spent) AS total_revenue,
	COUNT(transaction_id) AS total_sales,
	ROUND(SUM(total_spent) / COUNT(transaction_id), 2) AS average_ticket,
	ROUND(AVG(quantity), 2) AS units_per_sale
FROM sales;

-- 1.2 Por trimestre:
SELECT
	quarter || 'Q' AS quarter,
	SUM(total_spent) AS total_revenue,
	COUNT(transaction_id) AS total_sales,
	ROUND(SUM(total_spent) / COUNT(transaction_id), 2) AS average_ticket,
	ROUND(AVG(quantity), 2) AS units_per_sale
FROM sales
WHERE quarter IS NOT NULL
GROUP BY quarter
ORDER BY quarter ASC;