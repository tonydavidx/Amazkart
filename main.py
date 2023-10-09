from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
import csv
import pandas as pd
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

# Create Firefox options and set preferences to disable images
options = Options()
options.set_preference("permissions.default.image", 2)

# Path to the Firefox GeckoDriver executable
driver_path = "C:\programs\geckodriver.exe"  # Replace with the actual path

# Create a WebDriver instance with the options
driver = webdriver.Firefox(service=Service(driver_path), options=options)


# option = Options()
# # option.add_argument('--headless')

# driver = webdriver.Firefox(options=option)

# Replace 'your_input.csv' with the path to your CSV file
data_file = './products.csv'

products_data = []

with open(data_file, 'r') as csvfile:
    csv_reader = csv.DictReader(csvfile)
    for row in csv_reader:
        products_data.append(row)

for i in range(len(products_data)):
    link = products_data[i]['link']
    driver.get(link)

    current_price = int(products_data[i]['price'])
    price_to_pay = driver.find_element(By.CLASS_NAME, 'priceToPay')
    price_element = price_to_pay.find_element(
        By.CLASS_NAME, 'a-price-whole').text

    new_price = int(price_element.replace(',', ''))
    if new_price < current_price or new_price > current_price:
        products_data[i]['price'] = new_price


df = pd.DataFrame(products_data)
df.to_csv(data_file, index=False)

sleep(3)
driver.quit()
