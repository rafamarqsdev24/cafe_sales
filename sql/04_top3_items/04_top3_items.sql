-- 4. Quais itens mais faturam, e quanto os 3 primeiros representam do total?
SELECT 
	item,
	SUM(total_spent) AS total_revenue,
	ROUND(100 * SUM(total_spent) / SUM(SUM(total_spent)) OVER (), 2) || '%' AS revenue_percent,
	ROUND(100 * SUM(SUM(total_spent)) OVER (ORDER BY SUM(total_spent) DESC) / SUM(SUM(total_spent)) OVER (), 2) || '%' AS cumulative_percent
FROM sales
GROUP BY item
ORDER BY total_revenue DESC
LIMIT 3;