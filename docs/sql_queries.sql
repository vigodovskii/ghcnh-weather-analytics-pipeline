-- ============================================================
-- GHCNH Weather Analytics — Example Queries
-- Target table: weather_warehouse.weather_analytics
--   Partitioned by: observation_date (DAY)
--   Clustered by:   station, name
--
-- Replace <project_id> with your GCP project ID.
-- ============================================================


-- 1. Row count and date range check
SELECT
  COUNT(*)                 AS total_rows,
  MIN(observation_date)    AS earliest_date,
  MAX(observation_date)    AS latest_date,
  COUNT(DISTINCT station)  AS station_count
FROM `<project_id>.weather_warehouse.weather_analytics`;


-- 2. Average temperature and dew point per station per day
SELECT
  station,
  name,
  observation_date,
  ROUND(AVG(tmp), 2) AS avg_temperature_c,
  ROUND(AVG(dew), 2) AS avg_dew_point_c,
  COUNT(*)            AS observation_count
FROM `<project_id>.weather_warehouse.weather_analytics`
WHERE observation_date BETWEEN '2025-01-01' AND '2025-12-31'
GROUP BY station, name, observation_date
ORDER BY observation_date, station
LIMIT 100;


-- 3. Fog risk indicator — low temperature / dew-point spread
--    T-Td spread below 3 C signals potential fog or low cloud.
SELECT
  observation_date,
  station,
  name,
  ROUND(AVG(tmp - dew), 2) AS avg_td_spread_c,
  COUNT(*)                  AS observation_count
FROM `<project_id>.weather_warehouse.weather_analytics`
WHERE observation_date BETWEEN '2025-01-01' AND '2025-12-31'
  AND tmp IS NOT NULL
  AND dew IS NOT NULL
GROUP BY observation_date, station, name
HAVING avg_td_spread_c < 3
ORDER BY avg_td_spread_c ASC
LIMIT 100;


-- 4. Daily pressure averages per station
--    Low pressure systems are associated with adverse weather and flight delays.
SELECT
  station,
  name,
  observation_date,
  ROUND(AVG(slp), 2) AS avg_pressure_hpa,
  COUNT(*)            AS observation_count
FROM `<project_id>.weather_warehouse.weather_analytics`
WHERE observation_date BETWEEN '2025-01-01' AND '2025-12-31'
  AND slp IS NOT NULL
GROUP BY station, name, observation_date
ORDER BY avg_pressure_hpa ASC
LIMIT 100;


-- 5. ML feature matrix — one row per station-hour
--    Export this for model training or further analysis.
SELECT
  station,
  name,
  observation_timestamp,
  observation_date,
  latitude,
  longitude,
  elevation,
  tmp                 AS temperature_c,
  dew                 AS dew_point_c,
  (tmp - dew)         AS td_spread_c,
  slp                 AS sea_level_pressure_hpa,
  report_type,
  quality_control
FROM `<project_id>.weather_warehouse.weather_analytics`
WHERE observation_date BETWEEN '2025-01-01' AND '2025-12-31'
ORDER BY station, observation_timestamp;
