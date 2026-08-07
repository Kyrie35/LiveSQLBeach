-- alien_1.sql
-- Signal-to-Noise Quality Indicator (SNQI) by weather condition
-- SNQI = SnrRatio - 0.1 * ABS(NoiseFloorDbm)
-- Analyzable signals: SNQI > 0
-- Median uses lower-median: (COUNT(*)+1)/2 integer division position

WITH signal_weather AS (
    SELECT
        o.weathprofile,
        s.snrratio - 0.1 * ABS(s.noisefloordbm) AS snqi
    FROM signals s
    JOIN telescopes t ON s.telescref = t.telescregistry
    JOIN observatories o ON t.observstation = o.observstation
),
ranked AS (
    SELECT
        weathprofile,
        snqi,
        ROW_NUMBER() OVER (PARTITION BY weathprofile ORDER BY snqi) AS rn,
        COUNT(*) OVER (PARTITION BY weathprofile) AS cnt
    FROM signal_weather
)
SELECT
    sw.weathprofile,
    ROUND(AVG(sw.snqi), 2) AS avg_snqi,
    ROUND((
        SELECT r.snqi
        FROM ranked r
        WHERE r.weathprofile = sw.weathprofile
          AND r.rn = CAST((r.cnt + 1) / 2 AS INTEGER)
        LIMIT 1
    ), 2) AS median_snqi,
    SUM(CASE WHEN sw.snqi > 0 THEN 1 ELSE 0 END) AS analyzable_count
FROM signal_weather sw
GROUP BY sw.weathprofile
ORDER BY avg_snqi DESC;