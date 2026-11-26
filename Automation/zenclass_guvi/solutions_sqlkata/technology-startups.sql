-- Q1
SELECT * FROM tech_startups WHERE founded_year < 2010;

-- Q2
SELECT startup_name
FROM tech_startups
ORDER BY founded_year DESC
LIMIT 1;

-- Q3
SELECT * FROM tech_startups WHERE industry = 'E-commerce';

-- Q4
SELECT * FROM tech_startups WHERE LENGTH(startup_name) = (SELECT MAX(LENGTH(startup_name)) FROM tech_startups);

-- Q5
SELECT COUNT(*) FROM tech_startups WHERE headquarters = 'San Francisco, CA';
