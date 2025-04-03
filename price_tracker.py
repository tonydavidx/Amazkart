import os
import csv
import random
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from config import DATA_DIR, PRODUCTS_CSV, GECKODRIVER_PATH, HEADLESS


def initialize_driver():
    options = Options()
    options.set_preference("permissions.default.image", 2)
    if HEADLESS:
        options.add_argument("--headless")
    return webdriver.Firefox(
        service=FirefoxService(GeckoDriverManager().install()), options=options
    )


def load_products():
    products = []
    if os.path.exists(PRODUCTS_CSV):
        with open(PRODUCTS_CSV, "r") as f:
            reader = csv.DictReader(f)
            products = list(reader)
    return products


def save_products(products):
    with open(PRODUCTS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "price", "link"])
        writer.writeheader()
        writer.writerows(products)


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
