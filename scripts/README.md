# Scripts

This directory contains utility scripts for managing election data.

## add_uuid_to_candidates.py

This script adds unique UUIDs to all candidate records in the election data files.

### Usage

```bash
# From the project root
python3 scripts/add_uuid_to_candidates.py

# Or run directly (script is executable)
./scripts/add_uuid_to_candidates.py
```

### What it does

1. Scans all `candidates.json` files in `app/data/lok_sabha/` and `app/data/vidhan_sabha/`
2. Adds a unique UUID to each candidate record that doesn't already have one
3. Writes the updated data back to the files
4. Reports statistics on how many candidates were updated

### Features

- **Idempotent**: Safe to run multiple times - won't create duplicate UUIDs
- **Automatic discovery**: Finds all candidate files automatically
- **Non-destructive**: Only adds UUIDs, doesn't modify existing data
- **Progress reporting**: Shows which files are being processed

### Example Output

```
======================================================================
Adding UUIDs to Candidate Data
======================================================================

Found 3 candidate files

Processing app/data/lok_sabha/lok-sabha-2024/candidates.json...
  ⚠️  File is empty, skipping
Processing app/data/vidhan_sabha/DL_2025_ASSEMBLY/candidates.json...
  ✅ Updated 769 candidates
Processing app/data/vidhan_sabha/MH_2024/candidates.json...
  ✅ Updated 4424 candidates

======================================================================
✅ UUID Update Complete!
======================================================================
```

### When to use

- After scraping new election data
- When setting up the repository for the first time
- After manually editing candidate data files
