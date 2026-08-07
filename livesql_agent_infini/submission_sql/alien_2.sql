WITH computed AS (
  SELECT
    s.bwhz / (s.centerfreqmhz * 1000000.0) AS bfr,
    p.anomscore,
    CASE
      WHEN p.techsigprob * (1.0 - p.natsrcprob) * p.sigunique * (0.5 + CAST(p.anomscore AS REAL) / 10.0) < 0.25 THEN 'Low'
      WHEN p.techsigprob * (1.0 - p.natsrcprob) * p.sigunique * (0.5 + CAST(p.anomscore AS REAL) / 10.0) < 0.75 THEN 'Medium'
      ELSE 'High'
    END AS category_name
  FROM signals s
  JOIN signalprobabilities p ON s.signalregistry = p.signalref
),
grp_stats AS (
  SELECT
    category_name,
    AVG(CAST(anomscore AS REAL)) AS avg_anom
  FROM computed
  GROUP BY category_name
)
SELECT
  c.category_name,
  COUNT(*) AS signal_count,
  AVG(c.bfr) AS avg_bandwidth_to_frequency_ratio,
  SQRT(AVG((c.anomscore - g.avg_anom) * (c.anomscore - g.avg_anom))) AS stddev_anomaly_score
FROM computed c
JOIN grp_stats g ON c.category_name = g.category_name
GROUP BY c.category_name
ORDER BY
  CASE c.category_name
    WHEN 'Low' THEN 1
    WHEN 'Medium' THEN 2
    WHEN 'High' THEN 3
  END;