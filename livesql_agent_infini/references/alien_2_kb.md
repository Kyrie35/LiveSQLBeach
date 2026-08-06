# External Knowledge for alien_2

Use these domain definitions when writing the final SQLite query.

## [3] Technological Origin Likelihood Score (TOLS)

Description: Combines multiple factors to estimate likelihood of technological origin.

Definition: $\text{TOLS} = \text{TechSigProb} \times (1 - \text{NatSrcProb}) \times \text{SigUnique} \times (0.5 + \frac{\text{AnomScore}}{10})$, where values above 0.75 warrant further investigation as potential technosignatures.

## [51] Bandwidth-to-Frequency Ratio (BFR)

Description: Normalized signal width relative to its central frequency.

Definition: $\text{BFR} = \frac{\text{BwHz}}{\text{CenterFreqMhz} \times 1{,}000{,}000}$, used to characterize signal spread relative to its frequency band.

## [52] TOLS Category

Description: Classification of signals based on TOLS thresholds.

Definition: Categorized as 'Low' if TOLS < 0.25, 'Medium' if TOLS < 0.75, and 'High' otherwise.
