-- Q1
SELECT InstructorID, COUNT(*) AS NumberOfCourses
FROM CourseInstructor
GROUP BY InstructorID;

-- Q2
SELECT InstructorID, COUNT(*) AS CourseCount FROM CourseInstructor GROUP BY InstructorID ORDER BY CourseCount DESC LIMIT 1;

-- Q3
SELECT RoomNo, COUNT(*) AS NumberOfCourses
FROM CourseInstructor
GROUP BY RoomNo;
