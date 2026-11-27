-- Q1
SELECT StudentName, COUNT(CourseID) AS NumberOfCourses FROM StudentEnrollment GROUP BY StudentName;
