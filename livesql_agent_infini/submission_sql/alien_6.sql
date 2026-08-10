SELECT
  o.observstation AS observatory_name,
  COUNT(*) AS total_signal_count,
  AVG((sp.techsigprob * 4 + sp.biosigprob / 100 + sp.sigunique * 2 + sp.anomscore / 2) * (1 - sp.falseposprob)) AS avg_rpi,
  AVG((1 - sp.falseposprob) * sd.decodeconf * CASE WHEN (s.snrratio - 0.1 * ABS(s.noisefloordbm)) > 0 THEN (s.snrratio - 0.1 * ABS(s.noisefloordbm)) / 10 + 0.5 ELSE 0.1 END) AS avg_approx_ccs,
  COUNT(CASE WHEN (sp.techsigprob * 4 + sp.biosigprob / 100 + sp.sigunique * 2 + sp.anomscore / 2) * (1 - sp.falseposprob) > 3 THEN 1 END) AS high_priority_count,
  COUNT(CASE WHEN (1 - sp.falseposprob) * sd.decodeconf * CASE WHEN (s.snrratio - 0.1 * ABS(s.noisefloordbm)) > 0 THEN (s.snrratio - 0.1 * ABS(s.noisefloordbm)) / 10 + 0.5 ELSE 0.1 END > 0.8 THEN 1 END) AS high_confidence_count,
  COUNT(CASE WHEN (sp.techsigprob * 4 + sp.biosigprob / 100 + sp.sigunique * 2 + sp.anomscore / 2) * (1 - sp.falseposprob) > 3 AND (1 - sp.falseposprob) * sd.decodeconf * CASE WHEN (s.snrratio - 0.1 * ABS(s.noisefloordbm)) > 0 THEN (s.snrratio - 0.1 * ABS(s.noisefloordbm)) / 10 + 0.5 ELSE 0.1 END > 0.8 THEN 1 END) AS both_criteria_count
FROM signals s
JOIN signalprobabilities sp ON s.signalregistry = sp.signalref
JOIN signaldecoding sd ON s.signalregistry = sd.signalref
JOIN telescopes t ON s.telescref = t.telescregistry
JOIN observatories o ON t.observstation = o.observstation
GROUP BY o.observstation
ORDER BY both_criteria_count DESC;
