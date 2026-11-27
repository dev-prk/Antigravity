-- Q2
SELECT artist, AVG(price) AS average_price
FROM artworks
WHERE artist IN ('Salvador Dali', 'Vincent Van Gogh')
GROUP BY artist;
