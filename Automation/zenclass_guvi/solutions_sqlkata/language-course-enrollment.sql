-- Q3
SELECT COUNT(*) FROM GermanCourse WHERE StudentName NOT IN (SELECT StudentName FROM FrenchCourse);
