-- Q2
SELECT category, COUNT(*) as count
FROM drug_inventory
GROUP BY category;
