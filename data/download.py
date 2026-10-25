"""Check that the NF-UNSW-NB15-v2 dataset is in data/ and is not damaged."""

import hashlib
from pathlib import Path

# The data folder (the folder this script is in)
DATA_DIR = Path(__file__).resolve().parent

# File name and its official SHA1 checksum (from the dataset authors)
FILE_NAME = "NF-UNSW-NB15-v2.csv"
EXPECTED_SHA1 = "dde9a9e38009ec60121cbb4fd884bf2c7cf5c0b0"

# Message shown when the file is missing
DOWNLOAD_HELP = """
How to get the dataset:
1. Open https://staff.itee.uq.edu.au/marius/NIDS_datasets/
2. Download NF-UNSW-NB15-v2 (a zip file).
3. Unzip it inside the data/ folder.
4. Run this script again.
Dataset record: https://doi.org/10.48610/ffbb0c1
"""


def find_csv():
    # Look for the CSV file anywhere inside the data folder
    matches = list(DATA_DIR.rglob(FILE_NAME))
    if matches:
        return matches[0]
    return None


def sha1_of(path):
    # Compute the SHA1 of a file, reading 1 MB at a time
    sha1 = hashlib.sha1()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            sha1.update(chunk)
    return sha1.hexdigest()


def main():
    # Stop with help text if the file is missing
    path = find_csv()
    if path is None:
        print(f"{FILE_NAME} was not found in data/.")
        print(DOWNLOAD_HELP)
        raise SystemExit(1)

    # Compare the checksum with the official one
    print("Found:", path)
    print("Checking the file. This takes a few seconds.")
    actual = sha1_of(path)
    print("Expected SHA1:", EXPECTED_SHA1)
    print("Actual SHA1:  ", actual)

    if actual == EXPECTED_SHA1:
        print("OK: the file is complete and not damaged.")
    else:
        print("ERROR: the checksum does not match. Download the file again.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()