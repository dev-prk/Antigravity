-- Q1
SELECT * FROM room_bookings WHERE nights_stayed > 5;

-- Q2
SELECT room_type, SUM(nights_stayed) AS total_nights FROM room_bookings GROUP BY room_type;
