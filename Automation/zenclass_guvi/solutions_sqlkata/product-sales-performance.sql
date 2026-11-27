-- Q2
SELECT Product.ProductName, SUM(Sales.Quantity) FROM Product INNER JOIN Sales ON Product.ProductID = Sales.ProductID GROUP BY Product.ProductName;
