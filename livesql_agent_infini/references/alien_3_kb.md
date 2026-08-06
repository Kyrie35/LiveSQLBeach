# External Knowledge for alien_3

Use these domain definitions when writing the final SQLite query.

## [9] Lunar Interference Factor (LIF)

Description: Calculates the potential interference from lunar illumination on observations.

Definition: $\text{LIF} = (1 - \frac{\text{LunarDistDeg}}{180}) \times (1 - \text{AtmosTransparency})$, where higher values indicate more lunar interference. Values above 0.5 suggest significant lunar contamination in data.

## [53] High Lunar Interference Events

Description: Observations with significant lunar interference.

Definition: Events where the calculated LIF is greater than 0.5, indicating strong lunar contamination in the data.
