-- Q1
SELECT ProductName FROM Electronics
UNION
SELECT ProductName FROM Furniture;

-- Q2
SELECT ProductName FROM Electronics
UNION ALL
SELECT ProductName FROM Furniture;

-- Q3
SELECT ProductName FROM Electronics
INTERSECT
SELECT ProductName FROM Furniture;
