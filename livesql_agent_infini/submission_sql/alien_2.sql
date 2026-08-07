SELECT
  CASE
    WHEN p.TechSigProb * (1 - p.NatSrcProb) * p.SigUnique * (0.5 + p.AnomScore / 10.0) < 0.25 THEN 'Low'
    WHEN p.TechSigProb * (1 - p.NatSrcProb) * p.SigUnique * (0.5 + p.AnomScore / 10.0) < 0.75 THEN 'Medium'
    ELSE 'High'
  END AS tol_category,
  COUNT(*) AS signal_count,
  AVG(s.BwHz / (s.CenterFreqMhz * 1000000.0)) AS avg_bfr,
  AVG(p.AnomScore * p.AnomScore) - AVG(p.AnomScore) * AVG(p.AnomScore) AS anomaly_stddev
FROM Signals s
JOIN SignalProbabilities p ON s.SignalRegistry = p.SignalRef
GROUP BY tol_category;