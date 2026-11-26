-- Q1
SELECT * FROM travel_packages;

-- Q2
UPDATE travel_packages SET available_slots = available_slots - 5 WHERE package_name = 'Mountain Escape';

-- Q3
INSERT INTO travel_packages (id, package_name, destination, price, available_slots) VALUES (4, 'Cultural Tour', 'Japan', 100000.00, 20);

-- Q4
SELECT package_name FROM travel_packages ORDER BY price DESC LIMIT 1;

-- Q5
SELECT SUM(price * available_slots) FROM travel_packages;
