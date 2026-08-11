-- archeology_2.sql
-- Identify archaeological sites in Degradation Risk Zones
-- Degradation Risk Zone: presstat IN ('Poor','Critical') AND structstate != 'Stable'
-- Grain: one row per site-scanconservation pair

SELECT
    s.zoneregistry AS site_code,
    s.zonelabel AS site_name,
    sc.structstate AS structural_state,
    s.presstat AS preservation_status,
    'Degradation Risk Zone' AS risk_zone_category
FROM sites s
LEFT JOIN scanconservation sc ON s.zoneregistry = sc.zoneref
WHERE s.presstat IN ('Poor', 'Critical')
  AND sc.structstate != 'Stable'
ORDER BY site_code ASC;
