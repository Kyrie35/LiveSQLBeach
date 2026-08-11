SELECT
    sp.flowsoft AS processing_software,
    sp.flowstage AS processing_stage,
    ROUND(AVG(sp.flowhrs), 1) AS avg_processing_hours,
    ROUND(AVG(sp.proccpu), 0) AS avg_cpu_usage_pct,
    ROUND(AVG(sp.procgpu), 0) AS avg_gpu_usage_pct,
    ROUND(AVG(s.gbsize), 1) AS avg_data_size_gb,
    ROUND(AVG(s.gbsize * log10(COALESCE(pc.totalpts, 1000000)) / (sp.flowhrs * (sp.proccpu + sp.procgpu) / 200.0)), 1) AS avg_per,
    CASE WHEN AVG(s.gbsize * log10(COALESCE(pc.totalpts, 1000000)) / (sp.flowhrs * (sp.proccpu + sp.procgpu) / 200.0)) < 0.5
         THEN 'Bottleneck Detected'
         ELSE 'Efficient'
    END AS efficiency_status,
    COUNT(*) AS workflow_count
FROM scanprocessing sp
JOIN scans s ON sp.zoneref = s.zoneref
LEFT JOIN scanpointcloud pc ON s.arcref = pc.arcref
WHERE sp.flowhrs > 0
  AND (sp.proccpu + sp.procgpu) > 0
GROUP BY sp.flowsoft, sp.flowstage
ORDER BY
    CASE WHEN AVG(s.gbsize * log10(COALESCE(pc.totalpts, 1000000)) / (sp.flowhrs * (sp.proccpu + sp.procgpu) / 200.0)) < 0.5
         THEN 1 ELSE 2 END,
    avg_per ASC;
