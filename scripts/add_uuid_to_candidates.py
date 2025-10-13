#!/usr/bin/env python3
"""
Script to add UUIDs to existing candidate data files.

This script:
1. Reads all candidate JSON files
2. Generates a unique UUID for each candidate
3. Writes the updated data back to the files
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Any


def generate_candidate_uuid() -> str:
    """Generate a unique UUID for a candidate."""
    return str(uuid.uuid4())


def update_candidates_file(file_path: Path) -> None:
    """Update a candidates JSON file with UUIDs."""
    print(f"Processing {file_path}...")
    
    # Read the existing data
    with open(file_path, 'r', encoding='utf-8') as f:
        candidates = json.load(f)
    
    if not candidates:
        print(f"  ⚠️  File is empty, skipping")
        return
    
    # Track statistics
    updated_count = 0
    
    # Add UUID to each candidate if not already present
    for candidate in candidates:
        if 'uuid' not in candidate:
            candidate['uuid'] = generate_candidate_uuid()
            updated_count += 1
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(candidates, f, indent=4, ensure_ascii=False)
    
    print(f"  ✅ Updated {updated_count} candidates")


def main():
    """Main function to update all candidate files."""
    print("="*70)
    print("Adding UUIDs to Candidate Data")
    print("="*70 + "\n")
    
    # Define base path
    base_path = Path("app/data")
    
    # Find all candidates.json files
    candidate_files = []
    
    # Lok Sabha files
    lok_sabha_dir = base_path / "lok_sabha"
    if lok_sabha_dir.exists():
        for election_dir in lok_sabha_dir.iterdir():
            if election_dir.is_dir():
                candidates_file = election_dir / "candidates.json"
                if candidates_file.exists():
                    candidate_files.append(candidates_file)
    
    # Vidhan Sabha files
    vidhan_sabha_dir = base_path / "vidhan_sabha"
    if vidhan_sabha_dir.exists():
        for election_dir in vidhan_sabha_dir.iterdir():
            if election_dir.is_dir():
                candidates_file = election_dir / "candidates.json"
                if candidates_file.exists():
                    candidate_files.append(candidates_file)
    
    print(f"Found {len(candidate_files)} candidate files\n")
    
    # Process each file
    for file_path in candidate_files:
        update_candidates_file(file_path)
    
    print("\n" + "="*70)
    print("✅ UUID Update Complete!")
    print("="*70)


if __name__ == "__main__":
    main()
