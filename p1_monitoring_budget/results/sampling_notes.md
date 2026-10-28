# Sampling notes (Day 3)

## Stratified sampling at low budgets
Strata are protocol plus destination port class (261 strata in the test set). Each stratum keeps at least 1 flow.

249 of the 261 strata contain only attack flows. They hold 3,540 of the 28,516 attack flows in the test set.

At the 0.1% budget (about 717 flows) the 261 floor flows are mostly attacks. The attack share of the kept flows is 0.374 for stratified and 0.044 for uniform (seed 0).

This comes from the dataset: the attacks use rare protocol and port combinations. It is not a general advantage of stratified sampling. The policy uses only header fields, no labels.

## Host-keyed sampling
Only 293 (source, destination) pairs exist in the data, and the attacks sit in 40 of them. A pair is kept or dropped as a whole, so the kept share is far from the budget (0.57723 at a 0.5 budget, 0.0 at 0.1%). Recall moves in steps. The budgets for this policy are nominal. The realized rate is saved in every result row.

Numbers in this file come from checks on seed 0. The full run replaces them in the report.