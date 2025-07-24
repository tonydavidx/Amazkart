import datetime
import os
from config import BASE_DIR
from utils import is_github_actions

# Use os.path.join for cross-platform compatibility and define a constant for max entries
LAST_RUN_FILE = os.path.join(BASE_DIR, "lastrun.txt")
MAX_LOG_ENTRIES = 100


def last_run_today():
    """
    Checks if the script has already been run today on a local machine.
    Returns True if it has run today, False otherwise.
    """
    # On GitHub Actions, this check is not needed. Return True to prevent local-only logic.
    if is_github_actions():
        return True

    try:
        with open(LAST_RUN_FILE, "r", encoding="utf-8") as f:
            first_line = f.readline()
            if not first_line:
                return False  # File is empty

        # Extract date part from the first line (e.g., "23/07/2025")
        last_date_str = first_line.strip().split()[0]
        last_run_date = datetime.datetime.strptime(last_date_str, "%d/%m/%Y").date()

        return last_run_date == datetime.date.today()

    except (FileNotFoundError, ValueError, IndexError):
        # If file doesn't exist, is empty, or has a malformed date,
        # it's safe to assume it has not run today.
        return False


def save_last_run():
    """
    Saves the current timestamp to the log file, overwriting it and
    keeping only the most recent MAX_LOG_ENTRIES.
    """
    lines = []
    try:
        # Read existing lines if the file exists
        with open(LAST_RUN_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        # If file doesn't exist, `lines` will be an empty list.
        pass

    # Add the new timestamp to the beginning of the list
    new_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    lines.insert(0, new_time + "\n")

    # Keep only the most recent entries
    limited_lines = lines[:MAX_LOG_ENTRIES]

    # Write the updated and truncated list back to the file
    try:
        with open(LAST_RUN_FILE, "w", encoding="utf-8") as f:
            f.writelines(limited_lines)
        print(f"Last run time saved: {new_time}")
    except IOError as e:
        print(f"Error writing to last run file: {e}")
