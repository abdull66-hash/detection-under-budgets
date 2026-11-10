# Figure captions (checked against the printed plot data)

## Figure 1: fig1_recall_vs_budget
Flow-level attack recall against the budget (share of flow records kept) for four sampling policies. Random forest, TTL columns dropped, trained on the full training set (regime i). Uniform, stratified and attack-aware: mean over 5 seeds with a 95% bootstrap interval. Host-keyed: mean over 100 hash seeds, with the band showing the 2.5% to 97.5% range. At a 0.1% budget the band is 0 to 0 because 98 of the 100 hash seeds keep no attack flow, so the mean (0.0004) lies above it. Dashed line: recall equal to the budget. The budget axis is logarithmic. The recall axis is symlog so that 0 can be shown. The attack-aware policy uses labels through its scorer.

## Figure 2: fig2_campaign_vs_budget
Share of attack campaigns with at least one flow that was sampled and flagged, against the budget. A campaign is an (attack class, source IP, destination IP) group with at least 10 test flows (243 campaigns). Same model, regime and error bars as Figure 1. Dotted line: expected value for uniform sampling from the campaign sizes, 1 - (1 - p*r)^n averaged over the campaigns, with r = 0.9982. Dashed line: 90%. The budget axis is logarithmic. The host-keyed point at a 0.1% budget (0.0004) lies on the bottom axis.

## Figure 3: fig3_recall_vs_fpr
Attack recall against the false positive rate (share of benign test flows flagged) for budgets from 0.1% to 100%, mean over 5 seeds (host-keyed also uses its 5-seed mean, so it differs from Figures 1 and 2). Each point is one budget. The lowest budgets are at the lower left. Random forest, TTL columns dropped, regime (i). Dashed line: the same ratio of recall to false positive rate as the full model (budget 100%). Both axes are logarithmic. Points with zero recall or zero false alarms are not drawn (host-keyed at 0.1%). At a 0.1% budget the points rest on very few false alarms: about 1 flow per seed for uniform, 2 for stratified and 20 for the attack-aware policy.

## Figure 4: eda_class_balance
Number of flows per class in NF-UNSW-NB15-v2 (2,390,275 flows). The axis is logarithmic, so bar lengths are not proportional to the counts.

## Figure 5: eda_feature_distributions
Distribution of five flow features for benign and attack flows, on a log10(1 + value) scale. Density histograms from a random sample of 200,000 flows. Flow duration is 0 ms for most flows. All other durations are close to 4.29 million ms (about 6.63 on this scale), so the feature acts like a yes/no flag.