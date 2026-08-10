SELECT
    observstation,
    lunarstage AS moon_phase,
    ROUND(AVG((1 - lunardistdeg / 180.0) * (1 - atmostransparency)), 4) AS avg_lif,
    CAST(SUM(CASE WHEN (1 - lunardistdeg / 180.0) * (1 - atmostransparency) > 0.5 THEN 1 ELSE 0 END) AS INTEGER) AS high_interference_count
FROM observatories
GROUP BY observstation, lunarstage
ORDER BY avg_lif DESC;
