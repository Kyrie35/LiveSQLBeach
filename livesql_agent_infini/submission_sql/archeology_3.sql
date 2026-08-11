-- archeology_3.sql
-- Report: Each site's code, name, and average Environmental Suitability Index (ESI)
-- ESI = 100 - 2.5 × |AmbicTemp - 20| - |(HumePct - 50)/2|^1.5 - 600/(IllumeLux + 100)
-- Higher ESI indicates more favorable scanning conditions.

SELECT
    s.zoneregistry AS site_code,
    s.zonelabel AS site_name,
    AVG(
        100.0
        - 2.5 * ABS(se.ambictemp - 20.0)
        - POWER(ABS((se.humepct - 50.0) / 2.0), 1.5)
        - 600.0 / (se.illumelux + 100.0)
    ) AS avg_esi
FROM sites s
JOIN scanenvironment se ON se.zoneref = s.zoneregistry
GROUP BY s.zoneregistry, s.zonelabel
ORDER BY s.zoneregistry ASC;
