-- Q1
SELECT COUNT(*) AS total_enrollments FROM Enrollment;

-- Q2
SELECT COUNT(*) FROM Enrollment WHERE CourseName = 'DBMS';

-- Q3
SELECT CourseName, COUNT(*) AS EnrollmentCount
FROM Enrollment
GROUP BY CourseName;
