import os
import csv
from datetime import datetime

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.firefox.service import Service as FirefoxService
# from webdriver_manager.firefox import GeckoDriverManager
from config import DATA_DIR, PRODUCTS_CSV, HEADLESS


# def initialize_driver():
#     options = Options()
#     options.set_preference("permissions.default.image", 2)
#     options.set_preference(
#         "general.useragent.override",
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
#     )
#     options.set_preference("dom.webdriver.enabled", False)
#     options.set_preference("intl.accept_languages", "en-US,en")
#     if HEADLESS:
#         options.add_argument("--headless")
#     driver = webdriver.Firefox(
#         service=FirefoxService(GeckoDriverManager().install()), options=options
#     )
#     driver.execute_script(
#         "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
#     )

#     return driver


def load_products():
    products = []
    if os.path.exists(PRODUCTS_CSV):
        # Use newline='' for reading and writing CSV files and specify encoding
        with open(PRODUCTS_CSV, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # This handles a header like "a,b,c," which creates a `None` fieldname
            if None in reader.fieldnames:
                # Filter out None from fieldnames to prevent creating a {None: value} pair
                reader.fieldnames = [
                    field for field in reader.fieldnames if field is not None
                ]
            for row in reader:
                # Safely remove the None key from the row dict if it still exists
                row.pop(None, None)
                products.append(row)
    return products


def save_products(products):
    # Use a consistent set of fieldnames for writing
    fieldnames = ["name", "price", "status", "important", "link"]
    with open(PRODUCTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(products)


def format_title(title):
    text = title.replace('"', "").replace(":", "")
    sympols = ["(", ","]
    for sym in sympols:
        if sym in text:
            title = text.split(sym)[0]
            break
    title = title.split()[:8]
    title = " ".join(title)
    return title


def save_price_history(product_id, price):
    history_file = os.path.join(DATA_DIR, f"{product_id}.csv")
    current_datetime = datetime.now()
    timestamp_changed = current_datetime.strftime("%d-%m-%Y %H:%M:%S")
    timestamp_unchanged = current_datetime.strftime("%d-%m-%Y 00:00:00")

    # Create file if not exists
    if not os.path.exists(history_file):
        with open(history_file, "w") as f:
            f.write("datetime,price\n")
        with open(history_file, "a") as f:
            f.write(f"{timestamp_changed},{price}\n")
        return

    # Read last entry
    with open(history_file, "r") as f:
        lines = f.readlines()
        if len(lines) <= 1:  # Only header exists
            with open(history_file, "a") as f:
                f.write(f"{timestamp_changed},{price}\n")
            return

        last_entry = lines[-1].strip().split(",")
        last_price = int(last_entry[1])
        last_date = last_entry[0].split()[0]  # Extract date part only
        current_date = current_datetime.strftime("%d-%m-%Y")

    # Determine if we need to save and which timestamp to use
    save_entry = False
    timestamp_to_use = timestamp_changed

    if price != last_price:
        save_entry = True
    elif last_date != current_date:
        save_entry = True
        timestamp_to_use = timestamp_unchanged  # Same price, new day - use 00:00:00

    if save_entry:
        with open(history_file, "a") as f:
            f.write(f"{timestamp_to_use},{price}\n")
