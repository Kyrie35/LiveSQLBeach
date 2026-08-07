-- alien_5.sql
-- Breakdown of signal modulation types with at least 5 occurrences.
-- For each modulation type: modulation type, signal count, average MCS, average SNR,
-- and a JSON with per-signal MCS and SNR values.
--
-- MCS = ModIndex * (1 + SSM) * M_factor
-- SSM = (1 - |FreqDriftHzs| / (FreqMhz * 1000)) * (SigDurSec / (1 + DoppShiftHz / 1000))
-- M_factor: 2 for AM, 1.5 for FM, 1 for other

SELECT s.ModType, COUNT(*) AS signal_count,
    AVG(s.ModIndex * (1 + (1 - ABS(s.FreqDriftHzs)/(s.FreqMhz*1000)) * s.SigDurSec/(1 + s.DoppShiftHz/1000)) *
        CASE WHEN s.ModType = 'AM' THEN 2 WHEN s.ModType = 'FM' THEN 1.5 ELSE 1 END) AS avg_mcs,
    AVG(s.SnrRatio) AS avg_snr,
    JSON_GROUP_OBJECT(
        s.SignalRegistry,
        JSON_OBJECT(
            'mcs', s.ModIndex * (1 + (1 - ABS(s.FreqDriftHzs)/(s.FreqMhz*1000)) * s.SigDurSec/(1 + s.DoppShiftHz/1000)) *
                   CASE WHEN s.ModType = 'AM' THEN 2 WHEN s.ModType = 'FM' THEN 1.5 ELSE 1 END,
            'snr', s.SnrRatio
        )
    ) AS signal_details
FROM Signals s
WHERE s.ModType IS NOT NULL
GROUP BY s.ModType
HAVING COUNT(*) > 5;