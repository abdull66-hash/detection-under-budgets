# I will list the targets that are commands, not files
.PHONY: setup data test p1 p2 p3 all clean

# I will install all packages from my pinned requirements
setup:
	pip install -r requirements.txt

# I will download the datasets (script comes later)
data:
	python data/download.py

# I will run all my unit tests
test:
	python -m pytest -v

# I will run each project (these get filled in as I build them)
p1:
	@echo "Project 1 is not built yet"

p2:
	@echo "Project 2 is not built yet"

p3:
	@echo "Project 3 is not built yet"

# I will run everything
all: p1 p2 p3

# I will remove caches, but never my data
clean:
	rm -rf .pytest_cache __pycache__