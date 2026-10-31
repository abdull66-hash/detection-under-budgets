# Regime and policy notes (Day 4)

Numbers: random forest, TTL dropped, mean over 5 seeds (see `results_summary.csv`). Budget = share of flows kept. The minimum budgets are on a 7-point grid: the smallest tested budget from which detection stays at or above 0.9.

## Regime (i) and regime (ii)
- Recall and campaign detection are almost the same in both regimes (differences at most 0.007). Policy D at 1%: recall 0.0949 and 0.0931, primary campaign detection 0.9358 and 0.9333.
- The false positive rate of policy D is lower in regime (ii): 0.0010 against 0.0019 at 5%, and 0.0015 against 0.0023 at 10%. The other policies are the same. Likely reason (not tested): policy D keeps benign flows that look like attacks, and a model trained on that sample learns to separate them.
- Carela-Español and Barlet-Ros found that training on sampled data helped a lot. Here it changes little. Possible reason (not tested): this dataset is easy to separate, even with few attack flows.

## Campaign detection
- Uniform sampling: observed campaign detection is within 0.02 of the value from the formula 1 - (1 - p * r)^n, averaged over the real campaign sizes (r = 0.9982, the recall with no sampling). Under uniform sampling, campaign detection is explained by the campaign sizes (median 87 flows, primary definition), not by the model.
- Example, primary definition: at a 1% budget uniform recall is 0.0103, but 54.7% of the campaigns are detected.

## Policy D (attack-aware)
- Smallest budget with 90% primary campaign detection: policy D 1%, uniform 10%, stratified 10%, host-keyed 100%. Coarse: policy D 1%, uniform 5%, stratified 5%, host-keyed 50%.
- Recall at a 5% budget: policy D 0.4747, uniform 0.0500.
- Cost: the false positive rate at a 5% budget is 0.0019 for policy D and 0.0002 for uniform (regime i). Policy D keeps the benign flows that look most like attacks.
- Policy D uses labels: the scorer is trained with them. The scorer reads every flow, including the ones it drops, so policy D reduces what the detector receives, not what is looked at.
- Part of the gain may come from this dataset: the attacks use rare port and protocol combinations that the scorer can find. Stratified shows the same pattern at 0.1%.

## Stratified
- At 0.1%: primary campaign detection 0.2576 against 0.1070 for uniform, recall 0.0094 against 0.0010. At 1% the two are close (0.5753 and 0.5465). At 10% uniform is slightly higher (0.9588 and 0.9523). The gain is limited to the lowest budgets and comes from the attack-only strata.

## Host-keyed
- Only 293 host pairs exist. Recall is 0.0033 at 1% and 0.4368 at 50%. Primary campaign detection reaches 90% only at the full budget. Both regimes give the same campaign detection (0.0049 at 1%). The budgets are nominal: the realized rate differs from the budget.

## Limits
- 243 primary and 35 coarse campaigns in the test set. The test set and the campaigns are fixed, so the intervals show training and sampling randomness only.
- The models are near-perfect on full data, so recall under sampling is mostly set by how many attack flows are sampled.