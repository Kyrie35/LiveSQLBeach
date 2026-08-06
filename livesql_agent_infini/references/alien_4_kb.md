# External Knowledge for alien_4

Use these domain definitions when writing the final SQLite query.

## [4] Bandwidth-Frequency Ratio (BFR)

Description: Measures the proportion of bandwidth to center frequency, helping identify signal type.

Definition: $\text{BFR} = \frac{\text{BwHz}}{\text{CenterFreqMhz} \times 10^6}$, where narrow ratios ($<0.001$) often indicate technological signals while wider ratios suggest natural phenomena.

## [10] Technosignature

Description: Defines the concept of signals that indicate technological activity.

Definition: A signal with $\text{TechSigProb} > 0.7$, $\text{NatSrcProb} < 0.3$, and $\text{ArtSrcProb} < 50$ that exhibits narrow bandwidth ($\text{BFR} < 0.001$) and high information density ($\text{InfoDense} > 0.8$).

## [3] Technological Origin Likelihood Score (TOLS)

Description: Combines multiple factors to estimate likelihood of technological origin.

Definition: $\text{TOLS} = \text{TechSigProb} \times (1 - \text{NatSrcProb}) \times \text{SigUnique} \times (0.5 + \frac{\text{AnomScore}}{10})$, where values above 0.75 warrant further investigation as potential technosignatures.
