from email.mime.multipart import MIMEMultipart
import os
from pydoc import plain
import random
import smtplib
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
import csv
import pandas as pd
from selenium.webdriver.firefox.options import Options
from email.mime.text import MIMEText
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options


# Create Firefox options and set preferences to disable images
options = Options()
options.set_preference("permissions.default.image", 2)

options.add_argument('--headless')
driver_path = "C:/programs/geckodriver.exe"  # Replace with the actual path


# Create a WebDriver instance with the options
driver = webdriver.Firefox(service=Service(driver_path), options=options)


data_file = 'D:/Documents/python/amazkart/products.csv'
products_data = []

with open(data_file, 'r') as csvfile:
    csv_reader = csv.DictReader(csvfile)
    for row in csv_reader:
        products_data.append(row)

for i in range(len(products_data)):
    try:
        link = products_data[i]['link']
        driver.get(link)
        title = driver.find_element(By.ID, "productTitle").text[:75]
        # print(title)
        products_data[i]['name'] = title[:50]
        current_price = int(products_data[i]['price'])
        price_to_pay = driver.find_element(By.CLASS_NAME, 'priceToPay')
        price_element = price_to_pay.find_element(
            By.CLASS_NAME, 'a-price-whole').text

        new_price = int(price_element.replace(',', ''))

        if new_price < current_price:
            products_data[i]['price'] = new_price
            print(f'Price dropped for {products_data[i]["name"]}')

            message = MIMEMultipart()
            message['Subject'] = f'🤖 Price dropped for {title[0:30]}'
            message['From'] = os.getenv("WHC_FROM_EMAIL")
            message['To'] = os.getenv("WHC_TO_EMAIL")

            message.attach(
                MIMEText(f'Price for {title} dropped from {current_price} to {new_price}\n\n{link}', 'plain'))

            with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
                smtp.starttls()
                smtp.login(user=os.getenv("WHC_FROM_EMAIL"),
                           password=os.getenv("WHC_EMAIL_PASS"))
                smtp.send_message(message)

        if new_price > current_price:
            products_data[i]['price'] = new_price
            print(f'Price increased for {products_data[i]["name"]}')

        sleep(random.randint(1, 10))

    except Exception as e:
        print(e)
        print(f'error in link: {link}')

df = pd.DataFrame(products_data)
df.to_csv(data_file, index=False)

sleep(3)
driver.quit()
