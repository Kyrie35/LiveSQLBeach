# External Knowledge for alien_1

Use these domain definitions when writing the final SQLite query.

## [0] Signal-to-Noise Quality Indicator (SNQI)

Description: Combines SNR and noise floor to provide a unified signal quality metric.

Definition: $\text{SNQI} = \text{SnrRatio} - 0.1 \times |\text{NoiseFloorDbm}|$, where higher values indicate better detection quality. Positive values generally indicate analyzable signals.

## [50] Analyzable Signals

Description: Signals of sufficient quality to be considered useful for further analysis.

Definition: Signals with SNQI > 0 are considered analyzable.
