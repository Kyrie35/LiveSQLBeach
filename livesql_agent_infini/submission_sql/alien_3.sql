-- alien_3.sql
-- Analyze how lunar interference affects observations:
-- Show the current moon phase, average Lunar Interference Factor (LIF)
-- and count of high lunar interference events for each observatory,
-- sorted by average LIF in descending order.
--
-- LIF = (1 - LunarDistDeg/180) * (1 - AtmosTransparency)
-- High Lunar Interference Events: events where LIF > 0.5

SELECT
    TRIM(o.observstation) AS observatory_name,
    o.lunarstage AS moon_phase,
    AVG((1.0 - o.lunardistdeg / 180.0) * (1.0 - o.atmostransparency)) AS avg_lif,
    SUM(CASE WHEN (1.0 - o.lunardistdeg / 180.0) * (1.0 - o.atmostransparency) > 0.5 THEN 1 ELSE 0 END) AS high_lif_event_count
FROM observatories o
JOIN telescopes t ON o.observstation = t.observstation
JOIN signals s ON t.telescregistry = s.telescref
GROUP BY o.observstation, o.lunarstage
ORDER BY avg_lif DESC;