-- Q1
SELECT AVG(Price) AS OverallAveragePrice FROM Product;

-- Q2
SELECT Category, AVG(Price) AS AveragePrice FROM Product GROUP BY Category;

-- Q3
SELECT 
    Category,
    AVG(Price) AS AveragePrice
FROM 
    Product
GROUP BY 
    Category
HAVING 
    AVG(Price) > (SELECT AVG(Price) FROM Product);
