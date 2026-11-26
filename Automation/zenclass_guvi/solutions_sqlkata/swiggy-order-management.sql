-- Q1
SELECT * FROM orders;

-- Q2
SELECT quantity FROM orders WHERE item_name = 'Spring Rolls' AND order_date = '2024-09-11';

-- Q3
UPDATE orders SET quantity = 3 WHERE item_name = 'Margherita Pizza';
SELECT * FROM orders;

-- Q4
SELECT restaurant_name FROM orders WHERE id = 1;

-- Q5
SELECT * FROM orders WHERE order_date = '2024-09-10';
