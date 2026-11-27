-- Q2
SELECT category, SUM(quantity) AS total_quantity FROM electronics_stock GROUP BY category;
