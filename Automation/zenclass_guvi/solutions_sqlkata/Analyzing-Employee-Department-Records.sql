-- Q1
SELECT DepartmentName, COUNT(*) AS EmployeeCount
FROM EmployeeDepartment
GROUP BY DepartmentName;

-- Q2
SELECT DepartmentName, COUNT(*) AS EmployeeCount FROM EmployeeDepartment GROUP BY DepartmentName ORDER BY EmployeeCount DESC LIMIT 1;

-- Q3
SELECT EmployeeName FROM EmployeeDepartment WHERE DepartmentName = 'HR';
