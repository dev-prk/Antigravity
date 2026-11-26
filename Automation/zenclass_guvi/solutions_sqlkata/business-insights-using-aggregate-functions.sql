-- Q1
SELECT COUNT(*) AS TotalPeople FROM Person;

-- Q2
SELECT COUNT(MiddleName) FROM Person;

-- Q3
SELECT AVG(StandardCost) FROM Product WHERE StandardCost > 0;

-- Q4
SELECT AVG(Freight) AS AverageFreight
FROM SalesOrderHeader
WHERE TerritoryID = 4;

-- Q5
SELECT MAX(ListPrice) FROM Product;

-- Q6
SELECT SUM(pi.Quantity * p.ListPrice) AS TotalInventoryValue
FROM ProductInventory pi
JOIN Product p ON pi.ProductID = p.ProductID
WHERE p.ListPrice > 0;
