-- Q1
SELECT * FROM FoodOrder;

-- Q2
DELETE FROM FoodOrder WHERE OrderStatus = 'Completed';
SELECT * FROM FoodOrder;

-- Q3
SELECT * FROM FoodOrder WHERE OrderStatus = 'Preparing';
