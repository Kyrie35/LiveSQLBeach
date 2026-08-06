# External Knowledge for alien_7

Use these domain definitions when writing the final SQLite query.

## [1] Atmospheric Observability Index (AOI)

Description: Quantifies how conducive atmospheric conditions are for signal detection.

Definition: $\text{AOI} = \text{AtmosTransparency} \times (1 - \frac{\text{HumidityRate}}{100}) \times (1 - 0.02 \times \text{WindSpeedMs})$, where values closer to 1 indicate ideal observation conditions.

## [9] Lunar Interference Factor (LIF)

Description: Calculates the potential interference from lunar illumination on observations.

Definition: $\text{LIF} = (1 - \frac{\text{LunarDistDeg}}{180}) \times (1 - \text{AtmosTransparency})$, where higher values indicate more lunar interference. Values above 0.5 suggest significant lunar contamination in data.

## [13] Optimal Observing Window (OOW)

Description: Defines conditions when observational quality is maximized.

Definition: Time periods when $\text{AOI} > 0.85$, $\text{LunarStage}$ is 'New' or 'First Quarter', $\text{LunarDistDeg} > 45$, and $\text{SolarStatus}$ is 'Low' or 'Moderate'.
