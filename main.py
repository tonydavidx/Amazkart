import os
import random
from selenium.webdriver.common.by import By
import time
from price_tracker import (
    initialize_driver,
    load_products,
    save_products,
    save_price_history,
)
from email_sender import send_price_alert
from chart_generator import generate_chart_image

os.chdir("D:/Documents/Python/Amazkart")


def track_prices():
    driver = initialize_driver()
    products = load_products()

    try:
        for product in products:
            try:
                product_id = product["link"].split("/")[-1]
                driver.get(product["link"])

                # Get product details
                title = driver.find_element(By.ID, "productTitle")
                short_title = title.text.split()[:8]
                short_title = " ".join(short_title)
                product["name"] = short_title

                # Get current price
                price_element = driver.find_element(By.CLASS_NAME, "priceToPay")
                new_price = int(
                    price_element.find_element(
                        By.CLASS_NAME, "a-price-whole"
                    ).text.replace(",", "")
                )
                current_price = int(product["price"])

                if new_price < current_price:
                    print(f"Price dropped for {product['name']}")
                    # Price dropped - save and notify
                    save_price_history(product_id, new_price)
                    product["price"] = new_price

                    chart_path = generate_chart_image(
                        product_id, title, current_price, new_price
                    )
                    print(f"Chart generated at {chart_path}")
                    send_price_alert(product, current_price, new_price, chart_path)

                    print(f"Price dropped for {product['name']}")
                elif new_price > current_price:
                    # Price increased - just update
                    save_price_history(product_id, new_price)
                    generate_chart_image(product_id, title, current_price, new_price)
                    product["price"] = new_price
                    print(f"Price increased for {product['name']}")
                else:
                    save_price_history(product_id, new_price)
                    print(f"Price unchanged for {product['name']}")

                time.sleep(random.randint(1, 10))

            except Exception as e:
                import traceback

                print(
                    f"Error processing {product.get('name', 'unknown')}:\n{traceback.format_exc()}"
                )

    finally:
        driver.quit()
        save_products(products)


if __name__ == "__main__":
    track_prices()
