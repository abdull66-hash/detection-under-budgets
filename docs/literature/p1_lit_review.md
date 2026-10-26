# Project 1 literature review: monitoring budget

Last updated: 2026-10-24

## 1. How I did this review

I collected the papers in Zotero and read the open-access PDFs. I uploaded them to NotebookLM and Elicit and gave both tools the same questions (problem, method, data, what is sampled, policies, budgets, model, training and split, metrics, repeats, results, limits, dataset problems). I compared the two answers. When the tools disagreed, or a number looked odd, it was checked in the paper text.

Each paper has an evidence label:

- **[Full text]**: the key parts were checked in the paper text.
- **[Two tools]**: NotebookLM and Elicit both read the PDF. The abstract and basic details were checked. The other numbers come from the tools.
- **[Abstract]**: only the abstract was available. I use these only where a paper is a direct base for one of my design choices (the attack-aware sampler).

Papers I could not find or read are not in this review. I do not use any number that I could not trace to a source.

## 2. Papers at a glance

| Key | Paper | Topic | Evidence |
|---|---|---|---|
| Alikhanov 2022 | Investigating the Effect of Traffic Sampling on ML-Based NIDS | ML intrusion detection under packet sampling | Full text |
| Mai 2006 | Is Sampled Data Sufficient for Anomaly Detection? | Sampling schemes vs anomaly detectors | Full text |
| Carela 2009 and 2011 | Identification of Network Applications based on ML (report); Impact of sampling on NetFlow traffic classification (journal) | ML classification under sampling | Report: full text. Journal: abstract |
| Sadrhaghighi 2022 | FlowShark | Sampling system with an ML classifier test | Full text |
| Androulidakis 2008 and 2011 | Selective flow-based sampling; Two-stage selective sampling | Sampling that favours small flows | Abstract |
| Ha 2016 | Suspicious traffic sampling for intrusion detection in SDNs | Sampling under IDS capacity | Abstract |
| Zhang 2011 | Adaptive traffic sampling for botnet detection | Cheap first stage, DPI second stage | Abstract |
| Sarhan 2021 | Towards a Standard Feature Set for NIDS Datasets | My dataset | Full text |
| Arp 2022 | Dos and Don'ts of ML in Computer Security | Evaluation mistakes | Two tools |
| Engelen 2021 | Troubleshooting an Intrusion Detection Dataset (CICIDS2017) | Dataset label quality | Two tools |
| Pendlebury 2019 | TESSERACT | Spatial and time bias | Two tools |
| Duffield 2004 | Sampling for Passive Internet Measurement | Background on sampling | Two tools |
| Sadrhaghighi 2021 | SoftTap | Monitoring capacity and IDS recall | Two tools |
| Esmaeilian 2024 | Coordinated Sampling in SDNs with Dynamic Flow Rates | Sampling coverage | Two tools |

## 3. Notes on each paper

### A. Sampling and detection (closest to my question)

#### Alikhanov et al. 2022 [Full text]
- **Problem:** how packet sampling at the flow-export step changes the performance of ML intrusion detection.
- **Method and data:** CIC-IDS-2018 (13 attack types plus benign, 78 CICFlowMeter features). Packets are sampled inside the flow meter and flow records are built from the sampled packets. Four samplers: simple random (SRS), SketchFlow (SFS), sketch-guided (SGS) and fast filtered (FFS). Rates 1/10, 1/100, 1/1000. Classifiers: decision tree, random forest, CNN.
- **Metrics:** detection rate (DR) and false alarm rate (FAR) at flow level. The ground truth is all flows in the full trace, so a flow that is never sampled counts as missed. Class scores are macro-averaged. Classes are balanced in the training set only.
- **Results:** flow visibility loss of about 20%, 50% and 80% at 1/10, 1/100 and 1/1000. Random forest without sampling: DR 98.31%, FAR 0.01%. With SFS and random forest at 1/10: DR about 80%, FAR 0.5%. At 1/1000 the FAR is 0.03%, but 85% of the malicious flows are missed. SFS works best overall. SGS drops sharply between 1/100 and 1/1000.
- **Repeats:** the sampling experiments were repeated three times. A one-way ANOVA compares classifiers. No confidence intervals.
- **Limits (their own):** misuse detection only, one dataset, three rates, four samplers, three classifiers.
- **Things to watch:**
  - The paper contradicts itself on visibility at 1/10. The introduction and Sec. V-A say about 20% of malicious flows are lost. The conclusion says 50%. I use the Sec. V-A numbers.
  - The paper does not say clearly whether the models were trained on full or sampled data. Sec. IV-E says cross-validation was needed because sampling shrinks the classes, which suggests training and testing on sampled records. NotebookLM said "trained on unsampled data", but I could not find that in the text, so I do not use it.
- **How I use it:** closest paper. I copy its idea that missed flows count as undetected, its macro averaging and its rule to balance only the training set. Its numbers are for another dataset, so I use them for context, not for comparison.

#### Mai et al. 2006 [Full text]
- **Problem:** can sampled data still detect anomalies?
- **Method and data:** four schemes (random packet, random flow, smart sampling, sample-and-hold) applied to Tier-1 backbone packet traces from 2003 and 2004. Three detectors, none of them ML: a wavelet volume detector and two port-scan detectors (TRWSYN, TAPS).
- **Budget:** all schemes are set to keep about the same share of flows. Packet sampling intervals 10, 20, 50, 100, 200, 500, 1000.
- **Metrics:** success ratio (scanners found out of true scanners), false negative ratio, false positive ratio. These count sources, not packets.
- **Results:**
  - All four schemes make all three detectors worse.
  - Volume detector: 21 anomalies in the original trace. At 1.47% of flows, random flow sampling finds 13. The other three schemes find 1 each.
  - TRWSYN under random packet sampling: success ratio falls from 79.6% (no sampling) to 45.6% at interval 500. Random flow sampling falls by only about 15% over the same range.
  - Smart sampling and sample-and-hold favour big flows and miss the small flows that scanners use.
  - Packet sampling shortens flows, which creates false positives.
- **Limits:** not ML, not multi-class, old traces, scanner ground truth is a manual list.
- **How I use it:** (1) my budget p is the share of flow records kept, as in this paper. (2) It supports my hypothesis that size-biased sampling hurts attacks made of small flows. (3) Its scanner-level success ratio is the nearest thing to my campaign-level metric. (4) It shows that sampling flow records avoids the flow-shortening effect, so my results are closer to its random flow sampling than to packet sampling.

#### Carela-Español and Barlet-Ros (report, 2009) and Carela-Español et al. 2011 [report: full text; journal: abstract]
- **Problem:** classify network applications with ML when only sampled NetFlow data is available.
- **Method and data (report):** C4.5 decision tree. Six 15-minute traces from a university link, 1.3 to 2.2 million flows each. Labels from the L7-filter DPI tool. One trace for training. The year 2009 comes from the report number in its web address (traces were collected in December 2008).
- **Results (report):** accuracy 94.14% without sampling and 40.11% at 1/1000 packet sampling. With NetFlow v5 features: 89.9% without sampling and 36.38% at 1/10,000. A preliminary test at 1/10 shows that training on sampled data raised accuracy from 54.65% to 80.34%.
- **Limits (their own):** the L7-filter labels are noisy, one training trace, the sampled-training test is preliminary. At very low rates few flows are left.
- **Journal paper (abstract only):** adapts the method to NetFlow, studies the effect of sampling, and proposes an automatic ML process that improves accuracy under sampling. Citation: Computer Networks 55(5), 1083-1099.
- **How I use it:** this is the reason I run two training regimes (train on full data and test on sampled data, and train and test on sampled data). It also warns me to report how many flows and campaigns are left at 1% and 0.1%. The numbers above are from the report. I do not cite them as the journal's numbers.

#### FlowShark, Sadrhaghighi et al. 2022 [Full text of the evaluation]
- **Problem:** per-flow sampling in SDNs that keeps high flow visibility.
- **Method:** edge switches sample short flows locally and a controller plans the sampling of long flows.
- **ML test (Sec. IV-C):** traffic classification (Google, Amazon, YouTube, SSL, HTTP) with an SVC (RBF kernel, C=5), on a small Mininet network, target rate 0.1, 5 runs. Baseline: uniform packet sampling. The x-axis is the number of flows (10 to 55), not the sampling rate.
- **Metrics:** recall counts missed flows as errors. "Missed flows" are flows with no sampled packet.
- **Result:** up to 27% higher recall and 19% higher precision than uniform packet sampling.
- **Limits:** classification, not intrusion detection. No attack classes, no campaign results, no confidence intervals. The training regime is not stated.
- **How I use it:** it shows that sampling policy changes what an ML model sees. I use its "missed flows" idea. It does not answer my question.

#### Androulidakis and Papavassiliou 2008 and 2011 [Abstract]
- **2008 (IET Communications 2(3), 399-409):** a framework for preferential flow sampling that balances the volume of processed data against detection accuracy. Tested with a non-parametric change-point detector on realistic data. It improves detection and selects fewer flows.
- **2011 (Security and Communication Networks 4(6), 608-621):** a two-stage selective sampling approach that selects small flows, because small flows are often the source of attacks. Tested on a worm scenario with an entropy-based detector on campus traces. In several cases detection was even better than without sampling.
- **How I use it:** background for my attack-aware two-stage sampler. The idea of two-stage selective sampling already exists for non-ML detectors, so I do not claim the idea is new.

#### Ha et al. 2016 [Abstract]
- A sampling strategy for SDNs that uses the full inspection capacity of the IDS for malicious traffic while keeping the sampled volume below that capacity. An optimization problem sets the sampling rate for each switch. Simulation and experiments.
- **How I use it:** background for the attack-aware sampler (suspicion-based sampling under a capacity limit).

#### Zhang et al. 2011 [Abstract]
- A system that finds a few suspicious hosts (likely bots) with an adaptive packet sampling algorithm and a spatial-temporal flow correlation step, and forwards their traffic to DPI-based detectors. Proof of concept tested on real legitimate and botnet traces.
- **How I use it:** background for a cheap first stage followed by a detailed second stage.

### B. Dataset and method

#### Sarhan et al. 2021 [Full text]
- **What it is:** a 43-feature NetFlow v9 feature set, extracted with nProbe, and the NF-v2 datasets, including NF-UNSW-NB15-v2. Flows are labelled by matching their five identifiers (IPs, ports, protocol) to the published attack events.
- **Facts I checked:** 2,390,275 flows, 95,053 attacks (3.98%), 9 attack classes. They drop IDs, IPs, ports and timestamps before training. For NF-UNSW-NB15-v2 they also drop the TTL-based features because of their "extreme correlation" with the labels. Extra Trees classifier, 70/30 split, five cross-validation splits.
- **Their reference results for NF-UNSW-NB15-v2 (binary):** accuracy 99.73%, AUC 0.9845, F1 0.97, detection rate 97.07%, false alarm rate 0.16%. **Multi-class detection rate:** Analysis 30.89%, Backdoor 40.30%, DoS 29.57%, Exploits 80.41%, Fuzzers 80.57%, Generic 85.15%, Reconnaissance 80.02%, Shellcode 87.67%, Worms 85.98%.
- **Limits:** random split, labels depend on 5-tuple matching, and the paper does not list which features are "TTL-based".
- **How I use it:** it documents my dataset. It is my source for dropping IDs, IPs and ports. My own EDA found that MAX_TTL and MIN_TTL almost perfectly separate attacks from benign flows (single-column AUC about 0.997), so I follow the dataset authors and drop them in the main runs. Its results are my Day 2 sanity targets.

#### Arp et al. 2022 [Two tools]
- Ten common mistakes when using ML in security, found widespread in a review of 30 papers. From the authors' slides, the first six are: sampling bias, label inaccuracy, data snooping, spurious correlations, biased parameters, inappropriate baselines.
- **How I use it:** the TTL finding is a spurious correlation. I split before sampling to avoid data snooping. My label risk is covered by the label-quality check. I use PR-AUC and false positive rate because only about 4% of the flows are attacks.

#### Engelen et al. 2021 [Two tools]
- Finds problems in traffic generation, flow construction, feature extraction and labelling in CICIDS2017. More than 20% of the traces were rebuilt or relabelled.
- **How I use it:** NF-v2 labels also come from matching flow identifiers, so label noise is possible. That is my inference, not a finding. I add a label-quality check on the attack flows. Alikhanov et al. also found mismatches between attack schedules and flow IDs in CIC-IDS-2018.

#### Pendlebury et al. 2019 [Two tools]
- Shows that results are inflated by spatial bias (unrealistic class ratios) and time bias. The study is about Android malware.
- **How I use it:** I keep the natural class ratio (about 4% attacks) in the test set. My dataset has no timestamps, so a time split is impossible. I state this as a limitation.

### C. Context

#### Duffield 2004 [Two tools]
A review of sampling for passive Internet measurement. I use it as background and for sampling definitions in the report.

#### SoftTap, Sadrhaghighi et al. 2021 [Two tools]
Mirrors traffic with commodity switches. An IDS on top of SoftTap reaches up to 25% higher detection recall than port-over-subscription mirroring. The IDS is a signature detector for one malware string, not ML. I use it to motivate why monitoring capacity is limited.

#### Esmaeilian et al. 2024 (dSamp) [Two tools]
Coordinated sampling when flow rates change. Its method samples up to 10% more flows at a given rate. It measures flow coverage, not detection. I use it only as context.

## 4. What each paper already does

(a) ML detector on sampled data. (b) More than one sampler at the same budget. (c) Entity- or campaign-level result. (d) Labelled multi-class intrusion data.

| Paper | (a) | (b) | (c) | (d) |
|---|---|---|---|---|
| Alikhanov 2022 | yes | yes | no (flow level) | yes (CIC-IDS-2018) |
| Mai 2006 | no (non-ML) | yes | yes (scanner level) | no |
| Carela report | yes (classification) | no | no | no (application classes) |
| FlowShark | yes (classification) | yes | no | no |
| Sarhan 2021 | no sampling | no | no | yes |
| Others | not checked or not relevant | | | |

The Androulidakis, Ha and Zhang papers were read at abstract level only, so I leave them out of this table.

## 5. Gap statement (draft)

Sampling is used in networks because monitoring everything costs too much (Duffield 2004). Early work showed that sampling harms detectors. Mai et al. (2006) found that four sampling schemes lowered the success of volume and port-scan detectors, and that schemes biased toward big flows miss the small flows that attacks use. Carela-Español and Barlet-Ros showed that a decision-tree traffic classifier lost much of its accuracy under packet sampling, and that training on sampled data recovered part of it. Androulidakis and Papavassiliou, Ha et al. and Zhang et al. design samplers that favour small or suspicious flows so that a detector sees more attacks.

The closest work is Alikhanov et al. (2022). They sample packets from CIC-IDS-2018 at 1/10, 1/100 and 1/1000, compare four samplers and three ML classifiers, and score detection per flow while counting unseen flows as missed. They find that many malicious flows disappear and that detection and false alarms get worse.

My project asks a similar question in a different setup. The data is NF-UNSW-NB15-v2 (NetFlow records, nine attack classes). Sampling is applied to flow records, not packets. I compare uniform, host-keyed, stratified and attack-aware two-stage sampling at the same budget, from 100% down to 0.1%, and I train the models in two ways (on full data and on sampled data). I report flow-level recall and also campaign-level detection (at least one flow of an attack campaign is caught). All results use 5 seeds with bootstrap confidence intervals.

In the papers I read, I did not find a study that reports campaign-level detection for ML detectors under several sampling policies on a labelled multi-class flow dataset. The nearest idea is the scanner-level success ratio in Mai et al. I treat campaign-level detection as my own design choice and define it clearly in the README.

What I do not claim:
- that my study is the first of its kind
- that 0.1% is a new budget (Alikhanov et al. tested 1/1000)
- that attack-aware sampling is a new idea
- that sampling flow records reproduces packet sampling (flows are sampled after export)
- that the results hold on real networks

The dataset has no timestamps, only four attacker IPs, and a small number of campaigns.

## 6. Choices I take from the literature

1. **Budget:** p is the share of flow records kept (Mai 2006). I report how many flows and campaigns are left at every budget (Carela report, Alikhanov 2022).
2. **Missed flows** count as not detected. The false positive rate is computed over all benign test flows, so an unsampled benign flow is never a false alarm (Alikhanov 2022).
3. **Metrics:** macro-F1, per-class recall, PR-AUC, false positive rate, flow-level recall and campaign-level detection (Alikhanov 2022, Arp 2022).
4. **Class balancing** only in the training set (Alikhanov 2022). The test set keeps the natural class ratio (Pendlebury 2019).
5. **Two training regimes** (Carela report). I do not claim this as a difference to Alikhanov et al., because their regime is unclear.
6. **Features:** drop IDs, IPs and ports (Sarhan 2021). Drop the TTL features in the main runs and keep a second run with them (Sarhan 2021, my EDA).
7. **Day 2 sanity check:** my full-data binary baseline with TTL dropped should be in the range of Sarhan's binary numbers (detection rate 97.07%, false alarm rate 0.16%, F1 0.97). Their multi-class numbers are not comparable, because my per-class recall counts any attack flag, not the exact class.
8. **Label check:** look at the attack flows for odd cases (Engelen 2021, Alikhanov 2022).
9. **Small classes** (Worms has 164 flows): report counts next to every per-class result.

## 7. Things I cannot prove but must still handle

| # | Item | Why it cannot be proven | What I do | When |
|---|---|---|---|---|
| 1 | Why TTL separates attacks from benign flows | No paper explains it. Sarhan et al. only say "extreme correlation". | Main runs without TTL columns, second run with them, report both. The cause is called unknown. | Day 2 |
| 2 | Which columns count as "TTL-based" | The paper does not list them. | Drop MIN_TTL and MAX_TTL. Test DNS_TTL_ANSWER and MIN_IP_PKT_LEN the same way and decide from the results. | Day 2 |
| 3 | Why only 4 attacker IPs (175.45.176.0 to .3) send all attacks | The dataset papers I read do not say. | State it as a limitation. Report campaigns with two definitions. | Day 4 and report |
| 4 | Label quality | Labels come from matching flow identifiers to attack lists. Alikhanov et al. found such mismatches in CIC-IDS-2018. | Check the attack flows for odd cases (for example zero returned bytes) and report the counts. | Day 2 |
| 5 | Definition of a campaign | No paper I read defines it for ML detectors. | Define it in `p1.yaml` (done) and in the README. Report both definitions. | Day 4 |
| 6 | Flow-record sampling vs packet sampling | The dataset has no packets. | State it as a limitation. Compare with Mai's random flow sampling. Make no claim about packet effects. | Report |
| 7 | Training regime in Alikhanov et al. | The text is unclear. | Run both of my regimes. Do not claim this as a difference. | Day 3 and 4 |

## 8. Reference list

1. Alikhanov, J., Jang, R., Abuhamad, M., Mohaisen, D., Nyang, D., Noh, Y. (2022). Investigating the Effect of Traffic Sampling on Machine Learning-Based Network Intrusion Detection Approaches. IEEE Access 10, 5801-5823. DOI 10.1109/ACCESS.2021.3137318.
2. Mai, J., Chuah, C.-N., Sridharan, A., Ye, T., Zang, H. (2006). Is Sampled Data Sufficient for Anomaly Detection? ACM IMC, 165-176. DOI 10.1145/1177080.1177102.
3. Carela-Español, V., Barlet-Ros, P. (2009). Identification of Network Applications based on Machine Learning Techniques. UPC research report RR 2009/18. https://www.ac.upc.edu/RR/2009/18.pdf
4. Carela-Español, V., Barlet-Ros, P., Cabellos-Aparicio, A., Solé-Pareta, J. (2011). Analysis of the impact of sampling on NetFlow traffic classification. Computer Networks 55(5), 1083-1099.
5. Sadrhaghighi, S., Dolati, M., Ghaderi, M., Khonsari, A. (2022). FlowShark: Sampling for High Flow Visibility in SDNs. IEEE INFOCOM, 160-169.
6. Androulidakis, G., Papavassiliou, S. (2008). Improving network anomaly detection via selective flow-based sampling. IET Communications 2(3), 399-409. DOI 10.1049/iet-com:20070231.
7. Androulidakis, G., Papavassiliou, S. (2011). Two-stage selective sampling for anomaly detection: analysis and evaluation. Security and Communication Networks 4(6), 608-621.
8. Ha, T., Kim, S., An, N., Narantuya, J., Jeong, C., Kim, J., Lim, H. (2016). Suspicious traffic sampling for intrusion detection in software-defined networks. Computer Networks 109, 172-182. DOI 10.1016/j.comnet.2016.05.019.
9. Zhang, J., Luo, X., Perdisci, R., Gu, G., Lee, W., Feamster, N. (2011). Boosting the scalability of botnet detection using adaptive traffic sampling. ACM ASIACCS, 124-134. DOI 10.1145/1966913.1966930.
10. Sarhan, M., Layeghy, S., Portmann, M. (2021). Towards a Standard Feature Set for Network Intrusion Detection System Datasets. arXiv:2101.11315.
11. Arp, D., Quiring, E., Pendlebury, F., Warnecke, A., Pierazzi, F., Wressnegger, C., Cavallaro, L., Rieck, K. (2022). Dos and Don'ts of Machine Learning in Computer Security. USENIX Security, 3971-3988. arXiv:2010.09470.
12. Engelen, G., Rimmer, V., Joosen, W. (2021). Troubleshooting an Intrusion Detection Dataset: the CICIDS2017 Case Study. IEEE Security and Privacy Workshops, 7-12. DOI 10.1109/SPW53761.2021.00009.
13. Pendlebury, F., Pierazzi, F., Jordaney, R., Kinder, J., Cavallaro, L. (2019). TESSERACT: Eliminating Experimental Bias in Malware Classification across Space and Time. USENIX Security, 729-746.
14. Duffield, N. (2004). Sampling for Passive Internet Measurement: A Review. Statistical Science 19(3), 472-498. DOI 10.1214/088342304000000206.
15. Sadrhaghighi, S., Dolati, M., Ghaderi, M., Khonsari, A. (2021). SoftTap: A Software-Defined TAP via Switch-Based Traffic Mirroring. IEEE NetSoft, 303-311.
16. Esmaeilian, S., Dolati, M., Sadrhaghighi, S., Ghaderi, M. (2024). Coordinated Sampling in SDNs with Dynamic Flow Rates. CNSM 2024, 1-7. arXiv:2409.05966.
