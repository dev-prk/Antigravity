-- Q3
SELECT Department.DepartmentName, COUNT(Employee.EmployeeID) AS EmployeeCount FROM Department INNER JOIN Employee ON Department.DepartmentID = Employee.DepartmentID GROUP BY Department.DepartmentName;
