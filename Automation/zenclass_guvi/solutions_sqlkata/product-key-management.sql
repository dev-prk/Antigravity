-- Q1
SELECT * FROM Product;

-- Q2
SELECT * FROM Product WHERE Price > 100;

-- Q3
SELECT Category, AVG(Price) AS AveragePrice FROM Product GROUP BY Category;
