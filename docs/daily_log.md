# Daily log

## Project 1, Day 0
- Did: I created the repo, folder skeleton, virtual environment and .gitignore.
- Did: I wrote common/seed.py, metrics.py, plotting.py and io.py, each with unit tests.
- Result: all 10 unit tests pass with pytest.
- Failed: my first test run broke because metrics.py was not saved. I saved it and it passed.
- Did: I committed and pushed Day 0 to GitHub, and the skeleton is visible there.
- Next: I will start Project 1, Day 1 (literature review and data).


## Project 1, Day 1
- Did: I downloaded NF-UNSW-NB15-v2, checked its SHA1 against the official value, and wrote the EDA notebook (class balance, duplicates, feature distributions). There is no timestamp column.
- Found: only 4 source IPs send attacks. MAX_TTL and MIN_TTL almost perfectly separate attacks from benign flows, so the main runs drop them. At least 25% of attack flows return 0 bytes. Flow duration is 0 for most flows.
- Did: I read 14 papers, wrote the literature review and references.bib, and set up p1.yaml.
- Failed: some NotebookLM numbers were wrong (a DOI, a venue, a novelty claim). I checked them against the papers and fixed them.
- Next: Day 2. Write preprocess.py, split the data, train the baseline models, and run the TTL and label checks.