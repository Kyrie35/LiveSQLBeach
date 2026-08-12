-- archeology_7.sql
-- Each site's code, name, and average environmental metrics,
-- along with average ESI, ESI quartile, and ECCS classification.
--
-- ESI formula (Knowledge #7):
--   ESI = 100 - 2.5 * |ambictemp - 20| - |(humepct - 50) / 2|^1.5 - 600 / (illumelux + 100)
--
-- ECCS thresholds (Knowledge #50):
--   >85 = Optimal, 70-85 = Good, 50-70 = Acceptable, <50 = Challenging

SELECT
    site_code,
    site_name,
    avg_temperature,
    avg_humidity,
    avg_illumination,
    avg_esi,
    NTILE(4) OVER (ORDER BY avg_esi) AS esi_quartile,
    CASE
        WHEN avg_esi > 85 THEN 'Optimal Scanning Conditions'
        WHEN avg_esi >= 70 THEN 'Good Scanning Conditions'
        WHEN avg_esi >= 50 THEN 'Acceptable Scanning Conditions'
        ELSE 'Challenging Scanning Conditions'
    END AS eccs_classification
FROM (
    SELECT
        s.zoneregistry AS site_code,
        s.zonelabel AS site_name,
        AVG(se.ambictemp) AS avg_temperature,
        AVG(se.humepct) AS avg_humidity,
        AVG(se.illumelux) AS avg_illumination,
        AVG(
            100.0
            - 2.5 * ABS(se.ambictemp - 20.0)
            - POWER(ABS((se.humepct - 50.0) / 2.0), 1.5)
            - 600.0 / (se.illumelux + 100.0)
        ) AS avg_esi
    FROM scanenvironment se
    JOIN sites s ON se.zoneref = s.zoneregistry
    GROUP BY s.zoneregistry, s.zonelabel
) sub
ORDER BY site_code;
