-- 7. In-store e Takeaway são negócios diferentes? Quais itens mais faturam em cada um?
-- 7.1 Por canal:
SELECT
	location,
    SUM(total_spent) AS total_revenue,
    COUNT(transaction_id) AS total_sales,
    ROUND(AVG(total_spent), 2) AS average_ticket
FROM sales
WHERE location <> 'Not Specified'
GROUP BY location
ORDER BY total_revenue DESC;

-- 7.2 Por item em cada canal:
SELECT location,
       item,
       SUM(total_spent) AS total_revenue
FROM sales
WHERE location <> 'Not Specified'
  AND item <> 'Not Specified'
GROUP BY location, item
ORDER BY location, total_revenue DESC;