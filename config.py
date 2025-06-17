import os

# Path Configuration
# Get the absolute path of the directory where the script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PRODUCTS_CSV = os.path.join(DATA_DIR, "products.csv")

# Email Configuration
EMAIL_FROM = os.getenv("WHC_FROM_EMAIL")
EMAIL_TO = os.getenv("WHC_TO_EMAIL")
EMAIL_PASSWORD = os.getenv("WHC_EMAIL_PASS")

# Selenium Configuration
HEADLESS = True  # Set to True for headless mode
