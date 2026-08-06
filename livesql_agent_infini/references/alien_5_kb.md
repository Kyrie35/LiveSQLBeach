# External Knowledge for alien_5

Use these domain definitions when writing the final SQLite query.

## [7] Signal Stability Metric (SSM)

Description: Quantifies overall temporal and spectral stability of a signal.

Definition: $\text{SSM} = (1 - \frac{|\text{FreqDriftHzs}|}{\text{FreqMhz} \times 1000}) \times \frac{\text{SigDurSec}}{1 + \frac{\text{DoppShiftHz}}{1000}}$, where higher values indicate more stable signals typical of fixed transmitters.

## [30] Modulation Complexity Score (MCS)

Description: Quantifies the sophistication of signal modulation based on type and stability.

Definition: $\text{MCS} = \text{ModIndex} \times (1 + \text{SSM}) \times M_{\text{factor}}$, where $M_{\text{factor}}$ is 2 for $\text{ModType} = \text{'AM'}$, 1.5 for 'FM', and 1 for other types. Incorporates Signal Stability Metric (SSM) to weight stable modulations higher.
