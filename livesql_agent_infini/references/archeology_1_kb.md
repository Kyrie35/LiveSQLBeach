# External Knowledge for archeology_1

Use these domain definitions when writing the final SQLite query.

## [0] Scan Resolution Index (SRI)

Description: A sophisticated compound index measuring the overall resolution quality of a scan based on resolution and point density.

Definition: SRI = \frac{\log_{10}(ScanResolMm \times 10^3)}{\log_{10}(PointDense)} \times 5, \text{ where lower values indicate higher quality resolution and more balanced scanning parameters.}

## [1] Scan Coverage Effectiveness (SCE)

Description: Measures how effectively a scan covers its target area considering both coverage percentage and overlap redundancy.

Definition: SCE = CoverPct \times \left(1 + \frac{LapPct}{100} \times \left(1 - \frac{CoverPct}{100}\right)\right), \text{ where higher values indicate more effective coverage with appropriate overlap.}

## [3] Scan Quality Score (SQS)

Description: Comprehensive quality metric combining resolution, coverage, and noise factors with weighted importance.

Definition: SQS = \left(\frac{10}{SRI}\right)^{1.5} \times \left(\frac{SCE}{100}\right) \times \left(1 - \frac{NoiseDb}{30}\right)^2, \text{ where higher values indicate exponentially better overall scan quality with emphasis on resolution.}
