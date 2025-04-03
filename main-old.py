from datetime import date
from email.mime.multipart import MIMEMultipart
import os
import random
import smtplib
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
import csv
import pandas as pd
from selenium.webdriver.firefox.options import Options
from email.mime.text import MIMEText
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options


# Create Firefox options and set preferences to disable images
options = Options()
options.set_preference("permissions.default.image", 2)

options.add_argument("--headless")
driver_path = "C:/programs/geckodriver.exe"  # Replace with the actual path


# Create a WebDriver instance with the options
driver = webdriver.Firefox(
    service=FirefoxService(GeckoDriverManager().install()), options=options
)


data_file = "D:/Documents/python/amazkart/products.csv"
products_data = []

today_date = date.today().strftime("%d-%m-%Y")
print(today_date)

with open(data_file, "r") as csvfile:
    csv_reader = csv.DictReader(csvfile)
    for row in csv_reader:
        products_data.append(row)

for i in range(len(products_data)):
    try:
        link = products_data[i]["link"]
        product_id = products_data[i]["link"].split("/")[-1]
        driver.get(link)
        title = driver.find_element(By.ID, "productTitle").text[:75].replace(",", "")
        # print(title)
        products_data[i]["name"] = title[:50]
        current_price = int(products_data[i]["price"])
        price_to_pay = driver.find_element(By.CLASS_NAME, "priceToPay")
        price_element = price_to_pay.find_element(By.CLASS_NAME, "a-price-whole").text

        new_price = int(price_element.replace(",", ""))

        def save_price(product_id, new_price):
            pass
            # product_id_file = f"D:/Documents/Python/Amazkart/data/{product_id}.csv"
            # with open(product_id_file, "a") as data_file:
            #     # edata = data_file.readlines()
            #     # last_price = edata[-1].split(",")[1]
            #     # last_date = edata[-1].split(",")[0]
            #     # if new_price != last_price and today_date != last_date:
            #     data_file.write(f"{today_date},{new_price}\n")

        if new_price < current_price:
            save_price(product_id, new_price)
            products_data[i]["price"] = new_price
            print(f"Price dropped for {products_data[i]['name']}")

            message = MIMEMultipart()
            message["Subject"] = f"🤖 Price dropped for {title[0:30]}"
            message["From"] = os.getenv("WHC_FROM_EMAIL")
            message["To"] = os.getenv("WHC_TO_EMAIL")

            message.attach(
                MIMEText(
                    f"Price for {title} dropped from {current_price} to {new_price}\n\n{link}",
                    "plain",
                )
            )

            with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
                smtp.starttls()
                smtp.login(
                    user=os.getenv("WHC_FROM_EMAIL"),
                    password=os.getenv("WHC_EMAIL_PASS"),
                )
                smtp.send_message(message)

        if new_price > current_price:
            save_price(product_id, new_price)
            products_data[i]["price"] = new_price
            print(f"Price increased for {products_data[i]['name']}")

        sleep(random.randint(1, 10))

    except Exception as e:
        print(e)
        print(f"error in link: {link}\n {title}")

df = pd.DataFrame(products_data)
df.to_csv(data_file, index=False)

sleep(3)
driver.quit()
