-- Q1
SELECT COUNT(*) FROM employees;

-- Q2
UPDATE employees
SET position = 'Senior Designer', salary = 65000.00
WHERE name = 'Anil Kumar';

SELECT * FROM employees WHERE name = 'Anil Kumar';

-- Q3
DELETE FROM employees WHERE name = 'Pooja Verma';
SELECT * FROM employees;

-- Q4
SELECT SUM(salary) FROM employees;

-- Q5
INSERT INTO employees (id, name, position, salary, department) VALUES (4, 'Rakesh Iyer', 'Intern', 35000.00, 'Marketing');
SELECT * FROM employees WHERE name = 'Rakesh Iyer';
