-- Q4
SELECT locations.location_name, COUNT(user_checkins.id) AS checkin_count FROM locations LEFT JOIN user_checkins ON locations.id = user_checkins.location_id GROUP BY locations.id;
