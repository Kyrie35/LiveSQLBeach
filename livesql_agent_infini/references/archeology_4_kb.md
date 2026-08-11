# External Knowledge for archeology_4

Use these domain definitions when writing the final SQLite query.

## [33] Registration Accuracy Ratio (RAR)

Description: Evaluates registration accuracy relative to scan resolution using propagation of uncertainty principles.

Definition: RAR = \frac{ScanResolMm}{LogAccuMm \times \sqrt{1 + \frac{ErrValMm}{LogAccuMm}}}, \text{ where values > 1 indicate registration accuracy exceeds scan resolution, a desirable outcome for precise spatial analysis.}

## [44] Registration Confidence Level

Description: Classification system for registration confidence based on multiple factors and error propagation analysis.

Definition: A classification where 'High Confidence' registrations have RAR > 1.5 and LogMethod containing 'Target', where RAR is Registration Accuracy Ratio, 'Medium Confidence' have RAR between 1.0-1.5, and 'Low Confidence' have RAR < 1.0, determining appropriate use cases for spatial analysis and interpretive visualization.
