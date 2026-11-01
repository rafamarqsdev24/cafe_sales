-- 5. O faturamento de cada item vem de volume ou de preço?
SELECT item,
       price_per_unit,
       SUM(total_spent) AS total_revenue,
       SUM(quantity) AS total_units,
       RANK() OVER (ORDER BY SUM(total_spent) DESC) AS revenue_rank,
       RANK() OVER (ORDER BY SUM(quantity) DESC) AS units_rank
FROM sales
WHERE item <> 'Not Specified'
GROUP BY item, price_per_unit
ORDER BY revenue_rank;