-- Q1
SELECT Publisher, COUNT(*) AS TotalBooks
FROM Book
GROUP BY Publisher;

-- Q2
SELECT Publisher, AVG(Price) AS AveragePrice
FROM Book
GROUP BY Publisher;

-- Q3
SELECT AuthorName, COUNT(*) AS TotalBooks
FROM Author
JOIN BookAuthor ON Author.AuthorID = BookAuthor.AuthorID
GROUP BY AuthorName;

-- Q4
SELECT Publisher, SUM(Price) FROM Book GROUP BY Publisher;

-- Q5
SELECT AuthorName, COUNT(*) AS NumberOfBooks
FROM Author
JOIN BookAuthor ON Author.AuthorID = BookAuthor.AuthorID
GROUP BY AuthorName
HAVING COUNT(*) > 1;
