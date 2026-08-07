-- alien_8.sql
-- Scan for Narrowband Technological Marker (NTM) profiles
-- Classification based on spectral coherence (sigcoherence from signaldynamics)
-- BFR = BwHz / (CenterFreqMhz * 10^6)
-- Knowledge base tiers:
--   Strong NTM:  BFR < 0.0001 AND |FreqDriftHzs| < 0.1  AND spectral coherence >= 0.5
--   Moderate NTM: BFR < 0.0005 AND |FreqDriftHzs| < 0.5  AND spectral coherence >= 0.5
--   Not NTM:     all other signals

SELECT
    s.signalregistry AS signal_id,
    s.centerfreqmhz AS central_freq_mhz,
    s.freqdrifthzs AS freq_drift_hzs,
    s.bwhz / (s.centerfreqmhz * 1000000.0) AS bfr,
    CASE
        WHEN s.bwhz / (s.centerfreqmhz * 1000000.0) < 0.0001
             AND ABS(s.freqdrifthzs) < 0.1
             AND CAST(sd.sigcoherence AS REAL) >= 0.5
        THEN 'Strong NTM'
        WHEN s.bwhz / (s.centerfreqmhz * 1000000.0) < 0.0005
             AND ABS(s.freqdrifthzs) < 0.5
             AND CAST(sd.sigcoherence AS REAL) >= 0.5
        THEN 'Moderate NTM'
        ELSE 'Not NTM'
    END AS ntm_classification
FROM signals s
JOIN signaldynamics sd ON s.signalregistry = sd.signalref
ORDER BY
    CASE
        WHEN s.bwhz / (s.centerfreqmhz * 1000000.0) < 0.0001
             AND ABS(s.freqdrifthzs) < 0.1
             AND CAST(sd.sigcoherence AS REAL) >= 0.5
        THEN 0
        WHEN s.bwhz / (s.centerfreqmhz * 1000000.0) < 0.0005
             AND ABS(s.freqdrifthzs) < 0.5
             AND CAST(sd.sigcoherence AS REAL) >= 0.5
        THEN 1
        ELSE 2
    END,
    s.bwhz / (s.centerfreqmhz * 1000000.0) ASC;