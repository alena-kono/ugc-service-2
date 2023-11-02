CREATE DATABASE IF NOT EXISTS ugc_analytics;

CREATE TABLE IF NOT EXISTS ugc_analytics.ugc_film_views (
    user_id UUID,
    film_id UUID,
    progress_sec UInt32,
    timestamp TIMESTAMP
)
Engine=MergeTree()
ORDER BY (user_id, film_id, timestamp);
