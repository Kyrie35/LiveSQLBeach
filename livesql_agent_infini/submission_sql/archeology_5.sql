WITH
pc_agg AS (
  SELECT
    arcref,
    AVG(coverpct) AS coverpct,
    AVG(lappct) AS lappct,
    AVG(scanresolmm) AS scanresolmm,
    AVG(CAST(pointdense AS REAL)) AS pointdense,
    AVG(noisedb) AS noisedb
  FROM scanpointcloud
  GROUP BY arcref
),
reg_agg AS (
  SELECT
    arcref,
    AVG(logaccumm) AS logaccumm,
    AVG(errvalmm) AS errvalmm
  FROM scanregistration
  GROUP BY arcref
),
mesh_agg AS (
  SELECT
    zoneref,
    AVG(CAST(facetfaces AS REAL)) AS facetfaces,
    AVG(CAST(facetverts AS REAL)) AS facetverts,
    AVG(facetresmm) AS facetresmm,
    AVG(CAST(texpix AS REAL)) AS texpix,
    AVG(geomdeltamm) AS geomdeltamm
  FROM scanmesh
  GROUP BY zoneref
),
site_raw AS (
  SELECT
    s.zoneref,
    AVG(pc.coverpct) AS coverpct,
    AVG(pc.lappct) AS lappct,
    AVG(pc.scanresolmm) AS scanresolmm,
    AVG(pc.pointdense) AS pointdense,
    AVG(pc.noisedb) AS noisedb,
    AVG(r.logaccumm) AS logaccumm,
    AVG(r.errvalmm) AS errvalmm,
    AVG(m.facetfaces) AS facetfaces,
    AVG(m.facetverts) AS facetverts,
    AVG(m.facetresmm) AS facetresmm,
    AVG(m.texpix) AS texpix,
    AVG(m.geomdeltamm) AS geomdeltamm
  FROM scans s
  JOIN pc_agg pc ON s.arcref = pc.arcref
  JOIN reg_agg r ON s.arcref = r.arcref
  JOIN mesh_agg m ON s.zoneref = m.zoneref
  GROUP BY s.zoneref
),
site_metrics AS (
  SELECT
    zoneref,
    coverpct * (1.0 + lappct / 100.0 * (1.0 - coverpct / 100.0)) AS sce,
    LOG(scanresolmm * 1000.0) / LOG(pointdense) * 5.0 AS sri,
    facetfaces / (facetverts * POWER(facetresmm, 2)) * 1000.0 AS mcr,
    texpix / (POWER(facetfaces, 0.5) * facetresmm) * 0.01 AS tdi,
    facetfaces / (facetverts * POWER(facetresmm, 2)) * 1000.0
      * (texpix / (POWER(facetfaces, 0.5) * facetresmm) * 0.01 / 10.0)
      * (1.0 + EXP(-geomdeltamm)) AS mfs,
    POWER(10.0 / (LOG(scanresolmm * 1000.0) / LOG(pointdense) * 5.0), 1.5)
      * (coverpct * (1.0 + lappct / 100.0 * (1.0 - coverpct / 100.0)) / 100.0)
      * POWER(1.0 - noisedb / 30.0, 2) AS sqs,
    scanresolmm / (logaccumm * POWER(1.0 + errvalmm / logaccumm, 0.5)) AS rar,
    noisedb,
    scanresolmm AS sr,
    errvalmm AS ev
  FROM site_raw
),
site_adc AS (
  SELECT
    zoneref,
    sce,
    mfs,
    rar,
    sqs,
    noisedb,
    sr,
    ev,
    sqs * 0.4 + mfs * 0.4 + sce * 0.2 - 5.0 * POWER(noisedb / 10.0, 0.5) AS adc
  FROM site_metrics
)
SELECT
  si.zoneregistry AS site_code,
  si.zonelabel AS site_designation,
  ROUND(
    0.3 * sa.adc + 0.3 * sa.mfs + 0.2 * sa.rar + 0.2 * sa.sce
    - 2.0 * POWER(sa.ev / sa.sr, 0.5),
    2
  ) AS dpq
FROM site_adc sa
JOIN sites si ON sa.zoneref = si.zoneregistry
ORDER BY dpq DESC;