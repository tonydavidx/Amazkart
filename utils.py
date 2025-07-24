import os
import pandas as pd


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
