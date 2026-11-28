-- Q1
SELECT flight_id, origin, destination, capacity - booked_seats AS available_seats
FROM flights
WHERE capacity > booked_seats;
