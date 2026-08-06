# External Knowledge for alien_6

Use these domain definitions when writing the final SQLite query.

## [8] Research Priority Index (RPI)

Description: Helps researchers prioritize signals for follow-up based on multiple factors.

Definition: $\text{RPI} = (\text{TechSigProb} \times 4 + \frac{\text{BioSigProb}}{100} + \text{SigUnique} \times 2 + \frac{\text{AnomScore}}{2}) \times (1 - \text{FalsePosProb})$, where values above 3 indicate high research priority.

## [0] Signal-to-Noise Quality Indicator (SNQI)

Description: Combines SNR and noise floor to provide a unified signal quality metric.

Definition: $\text{SNQI} = \text{SnrRatio} - 0.1 \times |\text{NoiseFloorDbm}|$, where higher values indicate better detection quality. Positive values generally indicate analyzable signals.

## [36] Confirmation Confidence Score (CCS)

Description: Quantifies overall confidence in signal verification across multiple parameters.

Definition: $\text{CCS} = (1 - \text{FalsePosProb}) \times \text{DecodeConf} \times \text{ClassConf} \times (\text{SNQI} > 0 ? \frac{\text{SNQI}}{10} + 0.5 : 0.1)$, where SNQI (Signal-to-Noise Quality Indicator) provides a quality weighting factor.

## [47] CCS Approximation

Description: Simplified CCS calculation using direct signal-to-noise ratio values when full Signal-to-Noise Quality Indicator (SNQI) data is unavailable.

Definition: $(1 - \text{FalsePosProb}) \times \text{DecodeConf} \times (\text{SNR} - 0.1 \times |\text{NoiseFloorDbm}| > 0 ? \frac{\text{SNR} - 0.1 \times |\text{NoiseFloorDbm}|}{10} + 0.5 : 0.1)$

## [54] High Confidence Signals

Description: Signal with Confirmation Confidence Score (CCS) > 0.8, indicating high reliability.

Definition: Signals where $\text{CCS} > 0.8$
