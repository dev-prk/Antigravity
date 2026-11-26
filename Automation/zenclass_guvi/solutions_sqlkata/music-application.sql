-- Q1
SELECT * FROM music_playlists WHERE number_of_songs > 30;

-- Q2
SELECT * FROM music_playlists ORDER BY total_duration DESC LIMIT 1;

-- Q3
SELECT * FROM music_playlists WHERE created_by = 'Charlie';

-- Q4
SELECT AVG(number_of_songs) AS average_songs FROM music_playlists;
