-- alien_4.sql
-- Which observatory stations are discovering the most potential technosignatures?
-- Technosignature criteria (from alien_4_kb.md):
--   TechSigProb > 0.7
--   NatSrcProb < 0.3
--   ArtSrcProb < 50
--   BFR < 0.001  where BFR = BwHz / (CenterFreqMhz × 10^6)
--   InfoDense > 0.8
-- TOLS = TechSigProb × (1 - NatSrcProb) × SigUnique × (0.5 + AnomScore / 10)

SELECT
    o.observstation AS observatory_name,
    COUNT(*) AS technosignature_count,
    AVG(sp.techsigprob * (1.0 - sp.natsrcprob) * sp.sigunique * (0.5 + sp.anomscore / 10.0)) AS avg_tols,
    AVG(s.bwhz / (s.centerfreqmhz * 1000000.0)) AS avg_bfr,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM (
        SELECT 1
        FROM signals s2
        JOIN signalprobabilities sp2 ON s2.signalregistry = sp2.signalref
        JOIN signalclassification sc2 ON s2.signalregistry = sc2.signalref
        WHERE sp2.techsigprob > 0.7
            AND sp2.natsrcprob < 0.3
            AND sp2.artsrcprob < 50
            AND (s2.bwhz / (s2.centerfreqmhz * 1000000.0)) < 0.001
            AND sc2.infodense > 0.8
    )) AS pct_of_all_technosignatures
FROM signals s
JOIN signalprobabilities sp ON s.signalregistry = sp.signalref
JOIN signalclassification sc ON s.signalregistry = sc.signalref
JOIN telescopes t ON s.telescref = t.telescregistry
JOIN observatories o ON t.observstation = o.observstation
WHERE sp.techsigprob > 0.7
    AND sp.natsrcprob < 0.3
    AND sp.artsrcprob < 50
    AND (s.bwhz / (s.centerfreqmhz * 1000000.0)) < 0.001
    AND sc.infodense > 0.8
GROUP BY o.observstation
ORDER BY technosignature_count DESC;