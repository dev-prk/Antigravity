-- Q4
SELECT 
    trains.train_number,
    schedules.arrival_time
FROM
    trains
JOIN schedules ON trains.id = schedules.train_id
WHERE
    schedules.date = '2024-09-01'
ORDER BY
    schedules.arrival_time DESC
LIMIT 1;

-- Q5
SELECT 
    CASE CAST(strftime('%w', date) AS INTEGER)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END AS day_name,
    COUNT(*) AS count_of_trains
FROM schedules
GROUP BY day_name
ORDER BY day_name;
