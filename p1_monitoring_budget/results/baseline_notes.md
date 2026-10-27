# Baseline notes (Day 2)

Test set: 717,083 flows (30% of the data, natural class ratio, split fixed with seed 0). Models trained on the full training set (1,434,164 flows). Class weights are balanced and the threshold is 0.5. Numbers are mean over 5 seeds with a 95% bootstrap interval (see `baseline_table.csv`).

## Main run (TTL columns dropped)

| Model | Recall | False positive rate | PR-AUC |
|---|---|---|---|
| Random forest | 0.9982 [0.9981, 0.9984] | 0.0040 | 0.9928 |
| LightGBM | 0.9977 [0.9975, 0.9979] | 0.0041 | 0.9918 |
| Logistic regression | 0.9931 | 0.0168 | 0.6497 |

With TTL kept (sensitivity run), random forest gives recall 0.9984 and PR-AUC 0.9934, so the tree models barely change. Logistic regression changes more (PR-AUC 0.8266).

## Comparison with Sarhan et al.

Sarhan et al. report for NF-UNSW-NB15-v2 (Extra Trees, TTL features dropped, 70/30 split, 5 cross-validation splits): detection rate 97.07% and false alarm rate 0.16%.

My random forest has recall 99.8% and a false positive rate of 0.40%. This is the same range. My models flag more attacks and also more benign flows. The likely reasons are the balanced class weights, the fixed 0.5 threshold, and a different model. I do not compare the multi-class numbers, because my per-class recall counts any attack flag and theirs counts the exact class.

## Label check (see `label_check.csv`)

36,377 of 95,053 attack flows (38%) return zero bytes, against 0.7% of benign flows. In Analysis, Backdoor and Generic, more than 80% of the flows return zero bytes. These may be real probes or "attempted attack" flows, and I cannot prove which. All flows are kept. Flow duration is 0 ms for most flows in every class, so it carries almost no information.

## Column check (see `column_check_table.csv`)

Rule set before the run: a column carries the result if removing it lowers recall by more than 0.005 or PR-AUC by more than 0.01. Removing `MIN_IP_PKT_LEN`, `DNS_TTL_ANSWER`, or both changed recall by at most 0.0003 and never lowered PR-AUC. Both columns stay in the main run. Logistic regression was not tested.

## Limits

- Detection is easy here: the trees are almost perfect on full data. The sampling results will mostly show how many attack flows survive sampling.
- The split is fixed, so the confidence intervals show training randomness only. Logistic regression has no randomness, so its interval has zero width.
- The 164 Worms flows give wide uncertainty (49 in the test set).
- The cause of the TTL separation is unknown.