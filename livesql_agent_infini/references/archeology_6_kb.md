# External Knowledge for archeology_6

Use these domain definitions when writing the final SQLite query.

## [4] Mesh Complexity Ratio (MCR)

Description: Measures the topological complexity of a mesh relative to its resolution, helping identify overly complex or simplified archaeological models.

Definition: MCR = \frac{FacetFaces}{FacetVerts \times FacetResMm^2} \times 10^3, \text{ where higher values indicate more complex meshes for a given resolution, capturing finer archaeological details.}

## [13] High Fidelity Mesh

Description: Defines criteria for high-fidelity 3D mesh models in archaeological documentation suitable for analytical studies.

Definition: A mesh with MCR > 5.0, FacetResMm < 1.0, and GeomDeltaMm < 0.5, where MCR is the Mesh Complexity Ratio, capable of representing fine archaeological details and surface morphology.

## [53] Mesh Quality Classification

Description: A standardized system for categorizing archaeological site documentation based on the presence and quality of 3D mesh models.

Definition: A three-tier classification where 'Has High-Fidelity Meshes' indicates sites with at least one mesh meeting high-fidelity criteria, 'Standard Mesh Quality' indicates sites with meshes that don't meet high-fidelity standards, and 'No Mesh Data' indicates sites lacking 3D mesh documentation entirely. This classification helps prioritize additional documentation efforts and determines appropriate analytical approaches for different sites.
