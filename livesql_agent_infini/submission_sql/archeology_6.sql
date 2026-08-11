-- archeology_6.sql
-- LiveSQLBench: Comprehensive High Fidelity Mesh Classification Report
-- Domain definitions from archeology_6_kb.md:
--   MCR = FacetFaces / (FacetVerts × FacetResMm²) × 10³  (definition [4])
--   High Fidelity: MCR > 5.0 AND FacetResMm < 1.0 AND GeomDeltaMm < 0.5  (definition [13])
--   Mesh Quality Classification: Has High-Fidelity Meshes / Standard Mesh Quality / No Mesh Data  (definition [53])

WITH mesh_metrics AS (
  SELECT
    zoneref AS site_code,
    facetregistry AS mesh_id,
    (facetfaces * 1.0 / (facetverts * facetresmm * facetresmm)) * 1000.0 AS mcr,
    facetresmm,
    geomdeltamm,
    CASE WHEN (facetfaces * 1.0 / (facetverts * facetresmm * facetresmm)) * 1000.0 > 5.0
         AND facetresmm < 1.0
         AND geomdeltamm < 0.5
         THEN 1 ELSE 0 END AS is_high_fidelity
  FROM scanmesh
  WHERE facetverts > 0 AND facetfaces > 0
)
SELECT
  s.zoneregistry AS site_code,
  s.zonelabel AS side_name,
  COUNT(m.mesh_id) AS total_mesh_count,
  SUM(CASE WHEN m.is_high_fidelity = 1 THEN 1 ELSE 0 END) AS high_fidelity_mesh_count,
  ROUND(
    CAST(SUM(CASE WHEN m.is_high_fidelity = 1 THEN 1 ELSE 0 END) AS REAL)
    / NULLIF(COUNT(m.mesh_id), 0)
    * 100.0,
    2
  ) AS high_fidelity_proportion_pct,
  ROUND(CAST(AVG(m.mcr) AS REAL), 2) AS avg_mcr,
  ROUND(CAST(AVG(m.facetresmm) AS REAL), 2) AS avg_resolution_mm,
  ROUND(CAST(AVG(m.geomdeltamm) AS REAL), 2) AS avg_geometric_accuracy_mm,
  CASE
    WHEN COUNT(m.mesh_id) = 0 THEN 'No Mesh Data'
    WHEN SUM(CASE WHEN m.is_high_fidelity = 1 THEN 1 ELSE 0 END) > 0
      THEN 'Has High-Fidelity Meshes'
    ELSE 'Standard Mesh Quality'
  END AS mesh_quality_classification
FROM sites s
LEFT JOIN mesh_metrics m ON s.zoneregistry = m.site_code
GROUP BY s.zoneregistry, s.zonelabel
ORDER BY high_fidelity_proportion_pct DESC, high_fidelity_mesh_count DESC;
