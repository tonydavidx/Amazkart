import os
import pandas as pd
import re


def is_github_actions():
    """Check if the script is running in GitHub Actions."""
    return os.environ.get("GITHUB_ACTIONS") == "true"


def load_and_process_data(history_file):
    """Load and process data from csv history file."""
    if not os.path.exists(history_file) or os.path.getsize(history_file) == 0:
        return None

    df = pd.read_csv(history_file)
    if df.empty:
        return None

    df = df[df["price"] != "UNAVAILABLE"]
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["datetime"] = pd.to_datetime(
        df["datetime"], format="%d-%m-%Y %H:%M:%S", errors="coerce"
    )
    df = df.dropna(subset=["datetime", "price"])
    df = df.sort_values("datetime")

    return df if not df.empty else None


def parse_price_to_int(text: str) -> int | None:
    """Parse a price string from Amazon and return integer rupees.

    Handles formats like '₹1,019.90', '1,019', '1,019.00', and plain digits.
    Returns None if parsing fails.
    """
    if not text:
        return None
    s = str(text).strip()
    # Keep digits, commas and dots
    s = re.sub(r"[^0-9,\.]", "", s)
    if not s:
        return None

    try:
        # If both comma and dot present, assume comma is thousands sep and dot is decimal
        if "," in s and "." in s:
            s2 = s.replace(",", "")
            value = float(s2)
        else:
            # If only commas present, remove them (they're thousands separators)
            s2 = s.replace(",", "")
            value = float(s2)
        return int(round(value))
    except Exception:
        return None
