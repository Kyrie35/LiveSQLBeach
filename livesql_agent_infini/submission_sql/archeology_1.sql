-- archeology_1.sql
-- Per-site average Scan Quality Score (SQS) ranking
-- Formula per uploaded external knowledge document:
--   SRI = log10(ScanResolMm * 10^3) / log10(PointDense) * 5
--   SCE = CoverPct * (1 + LapPct/100 * (1 - CoverPct/100))
--   SQS = (10/SRI)^1.5 * (SCE/100) * (1 - NoiseDb/30)^2

SELECT
    s.zoneregistry AS site_code,
    s.zonelabel AS site_name,
    ROUND(AVG(
        POW(10.0 / (LOG(sca.scanresolmm * 1000.0) / LOG(sca.pointdense) * 5.0), 1.5)
        * (sca.coverpct * (1.0 + sca.lappct / 100.0 * (1.0 - sca.coverpct / 100.0)) / 100.0)
        * POW(1.0 - sca.noisedb / 30.0, 2.0)
    ), 2) AS avg_sqs
FROM sites s
JOIN scans sc ON sc.zoneref = s.zoneregistry
JOIN scanpointcloud sca ON sc.arcref = sca.arcref
GROUP BY s.zoneregistry, s.zonelabel
ORDER BY avg_sqs DESC;
