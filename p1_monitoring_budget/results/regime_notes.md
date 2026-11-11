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
- False alarms: at the same budget policy D raises more false alarms than uniform (190.7 against 20.9 per 100,000 benign flows at a 5% budget), and it finds about 9 times more attacks (recall 0.4747 against 0.0500). The precision of the flagged flows is the same: 0.912 for policy D, 0.908 for uniform and 0.912 for the full model at 5%. So policy D adds no false alarms per detection.
- Policy D at a 1% budget gives about the same recall and false alarms as uniform at 10% (recall 0.0949 against 0.0997, false alarms 37.8 against 40.9 per 100,000). The gain is fewer flows sent to the detector for the same detection, not better alerts.
- At a 50% budget policy D keeps 76% of the false alarms of the full model (303.4 of 398.0 per 100,000). Uniform keeps 50%.
- Stratified has higher precision at low budgets (0.948 at 1%, 0.927 at 5%). Likely reason (not tested): it adds attack flows from the attack-only strata without adding false alarms.
- These bullets: random forest, TTL dropped, regime (i), 5-seed means.
- Policy D uses labels: the scorer is trained with them. The scorer reads every flow, including the ones it drops, so policy D reduces what the detector receives, not what is looked at.
- Part of the gain may come from this dataset: the attacks use rare port and protocol combinations that the scorer can find. Stratified shows the same pattern at 0.1%.

## Stratified
- At 0.1%: primary campaign detection 0.2576 against 0.1070 for uniform, recall 0.0094 against 0.0010. At 1% the two are close (0.5753 and 0.5465). At 10% uniform is slightly higher (0.9588 and 0.9523). The gain is limited to the lowest budgets and comes from the attack-only strata.

## Host-keyed
- Only 293 host pairs exist. Recall is 0.0033 at 1% and 0.4368 at 50%. Primary campaign detection reaches 90% only at the full budget. Both regimes give the same campaign detection (0.0049 at 1%). The budgets are nominal: the realized rate differs from the budget.

## Limits
- 243 primary and 35 coarse campaigns in the test set. The test set and the campaigns are fixed, so the intervals show training and sampling randomness only.
- The models are near-perfect on full data, so recall under sampling is mostly set by how many attack flows are sampled.


## Host-keyed spread (100 hash seeds, one random forest, regime i)
- The test set has 286 host pairs. The mean recall over 100 hash seeds is close to uniform (0.0457 at 5%, 0.0968 at 10%, 0.4857 at 50%). The 5-seed mean of 0.4368 at 50% was within this spread, so it was chance.
- The spread is wide. Recall is 0 for 98% of the hash seeds at a 0.1% budget, 68% at 1%, 13% at 5% and 1% at 10%. At 10%, 95% of the hash seeds give recall between 0.0168 and 0.2065. At 50% they give 0.3366 to 0.6001.
- Realized rate: at a 0.1% budget it ranges from 0 to 0.0193, at 1% from 0 to 0.0585. The budget is nominal for this policy.
- Primary campaign detection is almost the same as recall, because the campaign key contains the same (source, destination) pair as the sampling key.
- Only one trained model (seed 0) was used, so the spread comes from the hash seed only.
- The host-keyed minimum budget for 90% campaign detection (primary 1.0, coarse 0.5) comes from the 5-seed run. The 100-hash-seed check covers only the primary definition.


## Other models (regime i, main run, 5-seed means)
- Recall and campaign detection at 1% and 5% budgets are about the same for logistic regression, random forest and LightGBM. Recall at 5%, uniform: 0.0499, 0.0500, 0.0500. Policy D: 0.4726, 0.4747, 0.4744.
- Logistic regression raises more false alarms: uniform at 5% gives 85.8 per 100,000 benign flows, against 20.9 for random forest and 21.9 for LightGBM.
- Keeping the TTL columns changes recall by at most 0.0001 for random forest, and false alarms by at most 1.5 per 100,000 (uniform at 5%: 20.9 without TTL, 20.2 with TTL).

## Recall for each attack class at a 5% budget (random forest, regime i)
- Uniform: 0.049 to 0.061 for every class. The highest is Worms (0.0612), with only 49 test flows.
- Policy D: Backdoor 0.931, Analysis 0.838, Worms 0.812, Fuzzers 0.645, DoS 0.611, Reconnaissance 0.586, Shellcode 0.464, Exploits 0.346, Generic 0.244.
- Policy D's gain is uneven. Generic and Exploits gain the least. The cause is not checked yet.
- With no sampling, recall is at least 0.990 for every class (lowest: Analysis, 0.9901).

## Lowest budgets (random forest, main run)
- At a 0.1% budget, uniform, stratified and policy D sample 714 to 717 flows. Host-keyed keeps 1,398 on average (nominal budget: 717).
- False alarms at 0.1%: uniform 0.17, stratified 0.23, policy D 2.88 per 100,000 benign flows, which is about 1, 2 and 20 flows. Results at 0.1% rest on very few false alarms.

## The attack-aware scorer (checked with inspect_scorer.py)
- The scorer is a depth-3 decision tree with 8 leaves. It is the same tree for seeds 0 to 4. It splits on 4 of the 5 listed fields: IN_PKTS (importance 0.593), L4_DST_PORT (0.294), TCP_FLAGS (0.085) and IN_BYTES (0.028). PROTOCOL is listed but never used.
- A flow's keep probability depends only on its leaf. At a 5% budget: leaf 3 is 1.0, leaf 11 is 0.861, leaf 10 is 0.056 and leaf 13 is 0.022.
- Leaf 3 (destination port <= 10, IN_BYTES <= 528, IN_PKTS <= 2.5) holds 3,602 test flows, 99.83% of them attacks (3,596 attack flows, 12.6% of the 28,516). Seven classes put 458 to 549 flows each into it: Analysis 536, Backdoor 481, DoS 532, Exploits 531, Fuzzers 549, Generic 509, Reconnaissance 458.
- Leaves 10 and 13 hold 685,949 of the 688,567 benign test flows (99.6%). They are 4.5% and 1.2% attacks.
- Per class, recall at a 5% budget follows the keep probabilities. Mean keep probability times recall without sampling is within 0.005 of the observed recall for 7 of 9 classes. Analysis is 0.0127 above (0.8250 expected, 0.8377 observed), cause not checked. Worms is 0.0343 above, with only 49 test flows, so chance can explain it.
- Generic (recall 0.244) and Exploits (0.346) gain little because 70% of the Generic flows (3,495 of 4,968) are in leaf 10 and 56% of the Exploits flows (5,332 of 9,465) are in leaf 13. These leaves are mostly benign. Backdoor and Analysis have 74% and 78% of their flows in leaf 3.
- A scorer that reads only 4 header fields cannot separate such attack flows from benign flows. A deeper scorer was not tested.