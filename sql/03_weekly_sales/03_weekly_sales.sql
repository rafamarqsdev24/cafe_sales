-- 3. Como as vendas se distribuem pela semana, e isso muda entre In-store e Takeaway?
SELECT 
	weekday,
	location,
	SUM(total_spent) AS total_revenue,
	COUNT(transaction_id) AS total_sales,
	ROUND(SUM(total_spent) / COUNT(transaction_id), 2) AS average_ticket,
	ROUND(AVG(quantity), 2) AS units_per_sale
FROM sales
WHERE location <> 'Not Specified' AND weekday IS NOT NULL 
GROUP BY weekday, location
ORDER BY ARRAY_POSITION(ARRAY['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'], weekday), total_sales DESC;