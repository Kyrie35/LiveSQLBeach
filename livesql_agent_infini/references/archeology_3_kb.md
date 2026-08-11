# External Knowledge for archeology_3

Use these domain definitions when writing the final SQLite query.

## [7] Environmental Suitability Index (ESI)

Description: Evaluates how suitable environmental conditions were for scanning operations using weighted parameters.

Definition: ESI = 100 - 2.5 \times \left|AmbicTemp - 20\right| - \left|\frac{HumePct - 50}{2}\right|^{1.5} - \frac{600}{IllumeLux + 100}, \text{ where higher values indicate more ideal scanning conditions adjusted for relative importance.}
