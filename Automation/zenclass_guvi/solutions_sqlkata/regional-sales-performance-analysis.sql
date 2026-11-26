-- Q1
SELECT TerritoryID, SUM(TotalDue) AS TotalSales
FROM SalesOrderHeader
GROUP BY TerritoryID
HAVING SUM(TotalDue) > 10000000;

-- Q2
SELECT s.Name, SUM(soh.TotalDue) AS TotalSales
FROM SalesTerritory s
JOIN SalesOrderHeader soh ON s.TerritoryID = soh.TerritoryID
GROUP BY s.TerritoryID, s.Name
HAVING SUM(soh.TotalDue) > 10000000;

-- Q3
SELECT Color, COUNT(*) AS ProductCount
FROM Product
GROUP BY Color
HAVING COUNT(*) >= 2;

-- Q4
SELECT Product.Name, SUM(SalesOrderDetail.OrderQty) AS TotalQuantity
FROM SalesOrderDetail
JOIN SalesOrderHeader ON SalesOrderDetail.SalesOrderID = SalesOrderHeader.SalesOrderID
JOIN Product ON SalesOrderDetail.ProductID = Product.ProductID
WHERE SalesOrderHeader.OrderDate LIKE '2006-%'
GROUP BY Product.Name
HAVING SUM(SalesOrderDetail.OrderQty) >= 200;

-- Q5
SELECT P.FirstName, P.LastName, COUNT(*) AS NumberOfOrders
FROM Customer C
JOIN Person P ON C.PersonID = P.BusinessEntityID
JOIN SalesOrderHeader SOH ON C.CustomerID = SOH.CustomerID
WHERE SOH.OrderDate >= '2005-07-01' AND SOH.OrderDate <= '2006-12-31'
GROUP BY C.CustomerID, P.FirstName, P.LastName
HAVING COUNT(*) >= 2
ORDER BY NumberOfOrders DESC;
