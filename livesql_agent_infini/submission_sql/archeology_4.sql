SELECT 
    r.logregistry AS registration_id,
    r.arcref AS project_id,
    r.logaccumm AS registration_accuracy_mm,
    r.errvalmm AS error_value_mm,
    ROUND(p.scanresolmm / (r.logaccumm * SQRT(1.0 + r.errvalmm / r.logaccumm)), 2) AS rar,
    r.logmethod AS logmethod,
    CASE 
        WHEN (p.scanresolmm / (r.logaccumm * SQRT(1.0 + r.errvalmm / r.logaccumm))) > 1.5 AND r.refmark LIKE '%Target%' THEN 'High Confidence'
        WHEN (p.scanresolmm / (r.logaccumm * SQRT(1.0 + r.errvalmm / r.logaccumm))) BETWEEN 1.0 AND 1.5 THEN 'Medium Confidence'
        ELSE 'Low Confidence'
    END AS confidence_level
FROM scanregistration r
INNER JOIN scanpointcloud p ON r.arcref = p.arcref
ORDER BY registration_id;
