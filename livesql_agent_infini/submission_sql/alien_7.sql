-- alien_7.sql
-- LiveSQLBench Base-Lite-SQLite: Observatory Conditions Report
-- Evaluates Atmospheric Observability Index (AOI) and Optimal Observing Window (OOW)

WITH station_metrics AS (
    SELECT
        TRIM(observstation) AS station,
        atmostransparency * (1.0 - humidityrate / 100.0) * (1.0 - 0.02 * windspeedms) AS aoi,
        lunarstage AS lunar_stage,
        lunardistdeg AS lunar_distance,
        solarstatus AS solar_status,
        CASE WHEN atmostransparency * (1.0 - humidityrate / 100.0) * (1.0 - 0.02 * windspeedms) > 0.85
             AND lunarstage IN ('New', 'First Quarter')
             AND lunardistdeg > 45
             AND solarstatus IN ('Low', 'Moderate')
        THEN 1 ELSE 0 END AS meets_oow
    FROM observatories
),
grouped AS (
    SELECT
        meets_oow,
        COUNT(*) AS station_count,
        ROUND(AVG(aoi), 3) AS avg_aoi,
        json_group_array(
            json_object(
                'station', station,
                'aoi', ROUND(aoi, 6),
                'lunar_factors', json_object(
                    'stage', lunar_stage,
                    'distance', ROUND(lunar_distance, 2)
                ),
                'solar_status', solar_status
            )
        ) AS station_details
    FROM station_metrics
    GROUP BY meets_oow
)
SELECT
    CASE WHEN meets_oow = 1 THEN 'True' ELSE 'False' END AS meets_oow,
    station_count,
    avg_aoi,
    station_details
FROM grouped
ORDER BY meets_oow DESC;