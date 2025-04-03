import os

# Path Configuration
DATA_DIR = "D:/Documents/Python/Amazkart/data"
PRODUCTS_CSV = os.path.join(DATA_DIR, "products.csv")

# Email Configuration
EMAIL_FROM = os.getenv("WHC_FROM_EMAIL")
EMAIL_TO = os.getenv("WHC_TO_EMAIL")
EMAIL_PASSWORD = os.getenv("WHC_EMAIL_PASS")

# Selenium Configuration
GECKODRIVER_PATH = "C:/programs/geckodriver.exe"
HEADLESS = False  # Set to True for headless mode
