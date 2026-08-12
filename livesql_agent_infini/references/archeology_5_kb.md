# External Knowledge for archeology_5

Use these domain definitions when writing the final SQLite query.

## [1] Scan Coverage Effectiveness (SCE)

Description: Measures how effectively a scan covers its target area considering both coverage percentage and overlap redundancy.

Definition: SCE = CoverPct \times \left(1 + \frac{LapPct}{100} \times \left(1 - \frac{CoverPct}{100}\right)\right), \text{ where higher values indicate more effective coverage with appropriate overlap.}

## [4] Mesh Complexity Ratio (MCR)

Description: Measures the topological complexity of a mesh relative to its resolution, helping identify overly complex or simplified archaeological models.

Definition: MCR = \frac{FacetFaces}{FacetVerts \times FacetResMm^2} \times 10^3, \text{ where higher values indicate more complex meshes for a given resolution, capturing finer archaeological details.}

## [5] Texture Density Index (TDI)

Description: Evaluates the pixel density of textures relative to mesh resolution for assessing surface detail preservation.

Definition: TDI = \frac{TexPix}{\sqrt{FacetFaces} \times FacetResMm} \times 10^{-2}, \text{ where higher values indicate more detailed textures relative to geometric complexity.}

## [6] Model Fidelity Score (MFS)

Description: Combines mesh complexity, texture quality, and geometric accuracy to assess overall 3D model fidelity for archaeological analysis.

Definition: MFS = MCR \times \left(\frac{TDI}{10}\right) \times \left(1 + \exp\left(-GeomDeltaMm\right)\right), \text{ where higher values indicate more accurate and detailed models with appropriate complexity.}

## [0] Scan Resolution Index (SRI)

Description: A sophisticated compound index measuring the overall resolution quality of a scan based on resolution and point density.

Definition: SRI = \frac{\log_{10}(ScanResolMm \times 10^3)}{\log_{10}(PointDense)} \times 5, \text{ where lower values indicate higher quality resolution and more balanced scanning parameters.}

## [3] Scan Quality Score (SQS)

Description: Comprehensive quality metric combining resolution, coverage, and noise factors with weighted importance.

Definition: SQS = \left(\frac{10}{SRI}\right)^{1.5} \times \left(\frac{SCE}{100}\right) \times \left(1 - \frac{NoiseDb}{30}\right)^2, \text{ where higher values indicate exponentially better overall scan quality with emphasis on resolution.}

## [9] Archaeological Documentation Completeness (ADC)

Description: Comprehensive score for how completely a site has been documented through scanning with weighted importance factors.

Definition: ADC = \left(SQS \times 0.4\right) + \left(MFS \times 0.4\right) + \left(SCE \times 0.2\right) - 5 \times \sqrt{\frac{NoiseDb}{10}}, \text{ where higher values indicate more complete documentation with multiple quality factors.}

## [33] Registration Accuracy Ratio (RAR)

Description: Evaluates registration accuracy relative to scan resolution using propagation of uncertainty principles.

Definition: RAR = \frac{ScanResolMm}{LogAccuMm \times \sqrt{1 + \frac{ErrValMm}{LogAccuMm}}}, \text{ where values > 1 indicate registration accuracy exceeds scan resolution, a desirable outcome for precise spatial analysis.}

## [38] Digital Preservation Quality (DPQ)

Description: Comprehensive metric for evaluating digital preservation quality for archaeological sites with weighted quality factors.

Definition: DPQ = (0.3 \times ADC) + (0.3 \times MFS) + (0.2 \times RAR) + (0.2 \times SCE) - 2 \times \sqrt{\frac{ErrValMm}{ScanResolMm}}, \text{ where ADC is Archaeological Documentation Completeness, MFS is Model Fidelity Score, RAR is Registration Accuracy Ratio, and SCE is Scan Coverage Effectiveness.}
