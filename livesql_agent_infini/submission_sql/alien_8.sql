SELECT
    SignalRegistry,
    CenterFreqMhz,
    FreqDriftHzs,
    BwHz / (CenterFreqMhz * 1000000) AS BFR,
    CASE
        WHEN BwHz / (CenterFreqMhz * 1000000) < 0.0001 AND FreqDriftHzs < 0.1 THEN 'Strong NTM'
        WHEN BwHz / (CenterFreqMhz * 1000000) < 0.0005 AND FreqDriftHzs < 0.5 THEN 'Moderate NTM'
        ELSE 'Not NTM'
    END AS ntm_classification
FROM signals
WHERE BwHz / (CenterFreqMhz * 1000000) < 0.001 AND FreqDriftHzs < 1.0
ORDER BY SignalRegistry;
