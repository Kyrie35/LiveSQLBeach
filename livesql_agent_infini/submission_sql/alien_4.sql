WITH tech_signals AS (
  SELECT
    t.observstation AS observatory_name,
    p.techsigprob * (1 - p.natsrcprob) * p.sigunique * (0.5 + p.anomscore / 10) AS tols,
    s.bwhz / (s.centerfreqmhz * 1000000) AS bfr
  FROM signals s
  JOIN signalprobabilities p ON s.signalregistry = p.signalref
  JOIN telescopes t ON s.telescref = t.telescregistry
  WHERE p.techsigprob > 0.7
    AND p.natsrcprob < 0.3
    AND p.artsrcprob < 50
    AND s.bwhz / (s.centerfreqmhz * 1000000) < 0.001
),
total_count AS (
  SELECT COUNT(*) AS total FROM tech_signals
)
SELECT
  ts.observatory_name,
  COUNT(*) AS technosignature_count,
  AVG(ts.tols) AS avg_tols,
  AVG(ts.bfr) AS avg_bfr,
  COUNT(*) * 100.0 / tc.total AS percentage_of_all_technosignatures
FROM tech_signals ts, total_count tc
GROUP BY ts.observatory_name
ORDER BY technosignature_count DESC;
