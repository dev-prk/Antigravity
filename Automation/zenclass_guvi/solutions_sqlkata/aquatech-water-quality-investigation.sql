-- Q1: Question 1  List all reservoirs where the water is alkaline (pH above 7.5).
SELECT reservoir_id, location, ph_level, turbidity, measurement_date FROM water_quality WHERE ph_level > 7.5 ORDER BY reservoir_id;
