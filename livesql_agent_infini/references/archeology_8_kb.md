# External Knowledge for archeology_8

Use these domain definitions when writing the final SQLite query.

## [8] Processing Efficiency Ratio (PER)

Description: Measures the efficiency of scan processing by comparing processing time to data complexity and size.

Definition: PER = \frac{GBSize \times \log_{10}(TotalPts)}{FlowHrs \times (ProcCPU + ProcGPU)/200}, \text{ where higher values indicate more efficient processing relative to data complexity.}

## [17] Processing Bottleneck

Description: Identifies processing workflows that are experiencing resource constraints using performance metrics.

Definition: A processing record with PER < 0.5, where PER is the Processing Efficiency Ratio, indicating potential hardware limitations affecting processing speed and output quality, requiring workflow optimization.
