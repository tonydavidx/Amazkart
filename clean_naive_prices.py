#!/usr/bin/env python3
"""Clean naive price parsing artifacts from CSV price history files.

Heuristics:
- If a price is >= 10000 and dividing by 100 produces a value within 0.1x-10x of the median, fix it by dividing by 100.
- Otherwise, if a price is >10x or <0.1x of the median historical price, drop the row as suspicious.

The script makes a .bak copy of each file it changes.
"""

import glob
import os
import shutil
import time
from typing import Tuple

import pandas as pd

from config import DATA_DIR


def process_file(path: str) -> Tuple[int, int]:
    """Process a single CSV file. Returns (corrected_count, removed_count)."""
    # Read file manually to avoid pandas tokenization errors from stray commas
    with open(path, "r", encoding="utf-8") as fh:
        lines = [ln.rstrip("\n") for ln in fh]
    if not lines:
        print(f"Skipping empty file {os.path.basename(path)}")
        return 0, 0

    header = lines[0].lower()
    if "price" not in header:
        print(f"Skipping {os.path.basename(path)} (no 'price' column in header)")
        return 0, 0

    rows = []
    for ln in lines[1:]:
        if not ln.strip():
            continue
        # split only on first comma to allow commas in datetime or other fields
        parts = ln.split(",", 1)
        if len(parts) < 2:
            # malformed
            continue
        dt, price_raw = parts[0].strip(), parts[1].strip()
        rows.append({"datetime": dt, "price": price_raw})

    df = pd.DataFrame(rows)

    # Keep original for backup if we change anything

    # Normalize numeric prices where possible
    df["price_num"] = pd.to_numeric(df["price"], errors="coerce")

    valid = df["price_num"].dropna()
    if valid.empty:
        print(f"Skipping {os.path.basename(path)} (no numeric prices)")
        return 0, 0

    median = valid.median()
    if median <= 0 or pd.isna(median):
        # not enough information to decide
        print(f"Skipping {os.path.basename(path)} (median not available)")
        return 0, 0

    corrected = 0
    removed = 0
    to_remove = []

    for idx, row in df.iterrows():
        p = row["price_num"]
        if pd.isna(p) or p <= 0:
            to_remove.append(idx)
            removed += 1
            continue

        # Candidate naive: very large integer likely produced by concatenating decimals
        if p >= 10000:
            p_div100 = int(round(p / 100.0))
            if median * 0.1 <= p_div100 <= median * 10:
                df.at[idx, "price_num"] = p_div100
                corrected += 1
                continue

        # If still extremely far from median, remove it
        if p > median * 10 or p < median * 0.1:
            to_remove.append(idx)
            removed += 1

    if corrected == 0 and removed == 0:
        print(f"No changes for {os.path.basename(path)}")
        return 0, 0

    # Backup original
    bak_path = f"{path}.bak-{int(time.time())}"
    shutil.copy2(path, bak_path)

    # Drop rows and write cleaned file
    if to_remove:
        df = df.drop(index=to_remove)

    # Ensure price column is integer when available
    df["price"] = df["price_num"].round().astype("Int64")
    # Drop helper column
    df = df.drop(columns=["price_num"]) if "price_num" in df.columns else df

    df.to_csv(path, index=False)

    print(
        f"Updated {os.path.basename(path)}: corrected={corrected}, removed={removed} (backup: {os.path.basename(bak_path)})"
    )
    return corrected, removed


def main():
    files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    total_corrected = 0
    total_removed = 0
    changed_files = 0

    for f in files:
        # Skip products list file (it has product metadata, not price history)
        if os.path.basename(f).lower() in ("products.csv", "products copy.csv"):
            continue

        corrected, removed = process_file(f)
        if corrected or removed:
            changed_files += 1
        total_corrected += corrected
        total_removed += removed

    print("\nSummary:")
    print(f"Files changed: {changed_files}")
    print(f"Total corrected entries: {total_corrected}")
    print(f"Total removed entries: {total_removed}")


if __name__ == "__main__":
    main()
