-- Q2: Question 2  Display the movies for which more than one ticket has been booked.
SELECT Movie.MovieName, COUNT(TicketBooking.BookingID) FROM Movie INNER JOIN TicketBooking ON Movie.MovieID = TicketBooking.MovieID GROUP BY Movie.MovieName HAVING COUNT(TicketBooking.BookingID) > 1;
