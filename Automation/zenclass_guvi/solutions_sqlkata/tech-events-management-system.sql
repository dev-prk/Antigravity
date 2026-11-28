-- Q1
SELECT COUNT(*) FROM tech_conferences WHERE location LIKE '%, USA' OR location IN ('San Francisco, USA', 'New York, USA');

-- Q2
SELECT * FROM tech_conferences WHERE organizer = 'TechWorld Inc.';
