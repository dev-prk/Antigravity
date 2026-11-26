-- Q1
SELECT * FROM Courier;

-- Q2
SELECT * FROM Courier WHERE DestinationCity = 'Chennai' OR DestinationCity = 'Salem';

-- Q3
SELECT * FROM Courier WHERE DestinationCity != 'Chennai' AND DestinationCity != 'Salem';
