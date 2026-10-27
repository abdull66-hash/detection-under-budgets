# Daily log

## Project 1, Day 0
- Did: I created the repo, folder skeleton, virtual environment and .gitignore.
- Did: I wrote common/seed.py, metrics.py, plotting.py and io.py, each with unit tests.
- Result: all 10 unit tests pass with pytest.
- Did: I committed and pushed Day 0 to GitHub, and the skeleton is visible there.
- Next: I will start Project 1, Day 1 (literature review and data).


## Project 1, Day 1
- Did: I downloaded NF-UNSW-NB15-v2, checked its SHA1 against the official value, and wrote the EDA notebook (class balance, duplicates, feature distributions). There is no timestamp column.
- Found: only 4 source IPs send attacks. MAX_TTL and MIN_TTL almost perfectly separate attacks from benign flows, so the main runs drop them. At least 25% of attack flows return 0 bytes. Flow duration is 0 for most flows.
- Did: I read 14 papers, wrote the literature review and references.bib, and set up p1.yaml.
- Next: Day 2. Write preprocess.py, split the data, train the baseline models, and run the TTL and label checks.


## Project 1, Day 2
- Did: I wrote preprocess.py (clean data, feature lists, stratified split into train, scorer and test) and models.py (logistic regression, random forest, LightGBM). I added 4 split tests. All 14 tests pass.
- Did: I trained the baselines on the full data with 5 seeds, for the main run (TTL dropped) and the sensitivity run (TTL kept). Random forest recall is 0.9982 and false positive rate is 0.0040. Dropping TTL changes the tree models very little.
- Found: 38% of attack flows return zero bytes, and more than 80% in Analysis, Backdoor and Generic. Flow duration is 0 ms for most flows. Removing MIN_IP_PKT_LEN or DNS_TTL_ANSWER changed recall by at most 0.0003, so both stay in.
- Next: Day 3. Write sampling.py with uniform, host-keyed and stratified policies, add unit tests, and run regime (i) across the budgets and seeds.