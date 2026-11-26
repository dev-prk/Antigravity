-- Q1
SELECT c.CustomerName, o.OrderAmount FROM Customer c INNER JOIN Orders o ON c.CustomerID = o.CustomerID;

-- Q2
SELECT c.CustomerName, SUM(o.OrderAmount) AS TotalOrderAmount
FROM Customer c
JOIN Orders o ON c.CustomerID = o.CustomerID
GROUP BY c.CustomerName;

-- Q3
SELECT c.CustomerName, SUM(o.OrderAmount) AS TotalOrderAmount
FROM Customer c
JOIN Orders o ON c.CustomerID = o.CustomerID
GROUP BY c.CustomerName
HAVING SUM(o.OrderAmount) > 700;
