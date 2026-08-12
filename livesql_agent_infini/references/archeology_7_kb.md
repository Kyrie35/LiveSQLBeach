# External Knowledge for archeology_7

Use these domain definitions when writing the final SQLite query.

## [7] Environmental Suitability Index (ESI)

Description: Evaluates how suitable environmental conditions were for scanning operations using weighted parameters.

Definition: ESI = 100 - 2.5 \times \left|AmbicTemp - 20\right| - \left|\frac{HumePct - 50}{2}\right|^{1.5} - \frac{600}{IllumeLux + 100}, \text{ where higher values indicate more ideal scanning conditions adjusted for relative importance.}

## [15] Optimal Scanning Conditions

Description: Defines the environmental conditions considered optimal for archaeological scanning based on instrument sensitivity profiles.

Definition: Conditions with ESI > 85, where ESI is the Environmental Suitability Index (knowledge #7), characterized by moderate temperature, humidity around 50%, and good illumination, minimizing environmental interference with scanning accuracy.

## [50] Environmental Condition Classification System (ECCS)

Description: A comprehensive classification system for archaeological site environments based on their suitability for scanning operations.

Definition: A four-tier classification where 'Optimal Scanning Conditions' have ESI > 85, 'Good Scanning Conditions' have ESI between 70-85, 'Acceptable Scanning Conditions' have ESI between 50-70, and 'Challenging Scanning Conditions' have ESI < 50. This classification guides scanning schedule planning and equipment selection to maximize data quality.
