-- Q1
SELECT * FROM produce WHERE category = 'Vegetable';

-- Q2
SELECT category, SUM(quantity) AS total_items FROM produce GROUP BY category;

-- Q3
UPDATE produce SET price = 45 WHERE item_name = 'Carrots';
SELECT * FROM produce WHERE category = 'Vegetable';

-- Q4
SELECT AVG(price) FROM produce;

-- Q5
DELETE FROM produce WHERE item_name = 'Potatoes';
