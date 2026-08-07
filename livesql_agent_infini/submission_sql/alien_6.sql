-- alien_6.sql: Observatories with most promising signals summary
-- RPI = (techsigprob * 4 + biosigprob / 100 + sigunique * 2 + anomscore / 2) * (1 - falseposprob)
-- CCS_approx = (1 - falseposprob) * decodeconf * CASE WHEN (snrratio - 0.1 * ABS(noisefloordbm)) > 0 THEN (snrratio - 0.1 * ABS(noisefloordbm)) / 10 + 0.5 ELSE 0.1 END
-- High priority: RPI > 3
-- High confidence: CCS_approx > 0.8

SELECT
    t.observstation,
    COUNT(*) AS total_signal_count,
    AVG((p.techsigprob * 4 + p.biosigprob / 100.0 + p.sigunique * 2 + p.anomscore / 2.0) * (1.0 - p.falseposprob)) AS avg_rpi,
    AVG((1.0 - p.falseposprob) * d.decodeconf *
        CASE
            WHEN (s.snrratio - 0.1 * ABS(s.noisefloordbm)) > 0
            THEN (s.snrratio - 0.1 * ABS(s.noisefloordbm)) / 10.0 + 0.5
            ELSE 0.1
        END) AS avg_ccs_approx,
    SUM(CASE WHEN (p.techsigprob * 4 + p.biosigprob / 100.0 + p.sigunique * 2 + p.anomscore / 2.0) * (1.0 - p.falseposprob) > 3 THEN 1 ELSE 0 END) AS high_priority_count,
    SUM(CASE WHEN (1.0 - p.falseposprob) * d.decodeconf *
            CASE
                WHEN (s.snrratio - 0.1 * ABS(s.noisefloordbm)) > 0
                THEN (s.snrratio - 0.1 * ABS(s.noisefloordbm)) / 10.0 + 0.5
                ELSE 0.1
            END > 0.8 THEN 1 ELSE 0 END) AS high_confidence_count,
    SUM(CASE WHEN (p.techsigprob * 4 + p.biosigprob / 100.0 + p.sigunique * 2 + p.anomscore / 2.0) * (1.0 - p.falseposprob) > 3
              AND (1.0 - p.falseposprob) * d.decodeconf *
                  CASE
                      WHEN (s.snrratio - 0.1 * ABS(s.noisefloordbm)) > 0
                      THEN (s.snrratio - 0.1 * ABS(s.noisefloordbm)) / 10.0 + 0.5
                      ELSE 0.1
                  END > 0.8 THEN 1 ELSE 0 END) AS both_criteria_count
FROM signals s
JOIN signalprobabilities p ON s.signalregistry = p.signalref
JOIN signaldecoding d ON s.signalregistry = d.signalref
JOIN telescopes t ON s.telescref = t.telescregistry
GROUP BY t.observstation
ORDER BY both_criteria_count DESC;