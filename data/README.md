# Data

The data files are never committed to git (see `.gitignore`).
Only this README, `download.py` and `checksums.txt` are tracked.

## NF-UNSW-NB15-v2 (primary dataset for Project 1)

- Source: University of Queensland (creator: Mohanad Sarhan), NetFlow version of UNSW-NB15
- Official page: https://staff.itee.uq.edu.au/marius/NIDS_datasets/
- Record and DOI: https://doi.org/10.48610/ffbb0c1
- File used: `NF-UNSW-NB15-v2.csv` (421.4 MB as downloaded)
- Feature list: `NetFlow_v2_Features.csv` (43 features per the paper)
- Reported size in the literature: 2,390,275 flows, about 96% benign (I will verify by counting rows myself)

### Licence and terms of access

The UQ eSpace record states: "Permitted Re-Use with Commercial Use Restriction".
- I acknowledge any re-use with the full citation shown on the eSpace record.
- I use the data for non-commercial research only.
- The "view license details" link on the record did not open when I tried it.

### How I downloaded it

1. I downloaded the zip from the official page above and extracted it.
2. I placed the extracted folder inside `data/`.
3. The CSV ends up at `data/<bag-folder>/<bag-folder>/data/NF-UNSW-NB15-v2.csv`.

### Citation (as shown on the UQ eSpace record)

```bibtex
@article{sarhan2023nf,
  title={NF-UNSW-NB15-v2},
  author={Sarhan, Mohanad and Layeghy, Siamak and Portmann, Marius},
  year={2023},
  publisher={The University of Queensland}
}
```

Record: https://doi.org/10.48610/ffbb0c1

The feature set is described in: Sarhan, Layeghy, Portmann, "Towards a Standard Feature Set for Network Intrusion Detection System Datasets", arXiv:2101.11315.

### To do

- Add the SHA1 checksum of the CSV to `checksums.txt`.