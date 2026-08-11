# External Knowledge for archeology_2

Use these domain definitions when writing the final SQLite query.

## [26] StructState (Structural State)

Description: Illustrates structural state classifications in archaeological conservation.

Definition: A categorical assessment with specific values: 'Stable' indicates structures that maintain integrity under normal conditions, 'Unstable' indicates structures showing signs of deterioration requiring intervention, and 'Critical' indicates structures at imminent risk of collapse requiring emergency stabilization.

## [14] Degradation Risk Zone

Description: Identifies archaeological sites at risk of degradation requiring urgent conservation intervention based on multiple factors.

Definition: A site with PresStat containing 'Poor' or 'Critical' and StructState not containing 'Stable', signaling immediate conservation needs due to active deterioration processes.

## [52] Risk Zone Category

Description: Classification system that evaluates archaeological sites for degradation risk based on preservation status and structural condition.

Definition: Categorizes archaeological sites into two main groups: 'Degradation Risk Zone' and 'Not in Risk Zone'. 'Not in Risk Zone' means that the site is not in a Degradation Risk Zone.
