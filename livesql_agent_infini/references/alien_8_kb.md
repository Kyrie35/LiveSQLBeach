# External Knowledge for alien_8

Use these domain definitions when writing the final SQLite query.

## [4] Bandwidth-Frequency Ratio (BFR)

Description: Measures the proportion of bandwidth to center frequency, helping identify signal type.

Definition: $\text{BFR} = \frac{\text{BwHz}}{\text{CenterFreqMhz} \times 10^6}$, where narrow ratios ($<0.001$) often indicate technological signals while wider ratios suggest natural phenomena.

## [15] Narrowband Technological Marker (NTM)

Description: Identifies a specific signature associated with technological transmission.

Definition: Signals with extremely narrow bandwidth ($\text{BFR} < 0.0001$), stable frequency ($\text{FreqDriftHzs} < 0.1$).

## [39] NTM Classification System

Description: A tiered classification system for Narrowband Technological Markers based on signal characteristics.

Definition: Three-tier classification: 'Strong NTM' (BFR < 0.0001 AND FreqDriftHzs < 0.1 AND non-natural modulation), 'Moderate NTM' (BFR < 0.0005 AND FreqDriftHzs < 0.5 AND non-natural modulation), and 'Not NTM' (all other signals).
