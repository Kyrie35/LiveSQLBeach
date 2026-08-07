SELECT
    CASE
        WHEN p.techsigprob * (1.0 - p.natsrcprob) * p.sigunique * (0.5 + p.anomscore / 10.0) < 0.25 THEN 'Low'
        WHEN p.techsigprob * (1.0 - p.natsrcprob) * p.sigunique * (0.5 + p.anomscore / 10.0) < 0.75 THEN 'Medium'
        ELSE 'High'
    END AS tol_category,
    COUNT(*) AS signal_count,
    AVG(s.bwhz / (s.centerfreqmhz * 1000000.0)) AS avg_bfr,
    AVG(p.anomscore * p.anomscore) - AVG(p.anomscore) * AVG(p.anomscore) AS anomaly_stddev
FROM signals s
JOIN signalprobabilities p ON s.signalregistry = p.signalref
GROUP BY tol_category
ORDER BY tol_category;
