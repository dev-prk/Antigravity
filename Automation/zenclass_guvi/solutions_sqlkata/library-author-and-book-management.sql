-- Q3
SELECT Author.AuthorName, COUNT(Book.BookID) AS BookCount
FROM Author
INNER JOIN Book ON Author.AuthorID = Book.AuthorID
GROUP BY Author.AuthorID, Author.AuthorName
HAVING COUNT(Book.BookID) > 1;
