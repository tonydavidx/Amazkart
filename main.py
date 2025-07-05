import asyncio
import random
from selenium.webdriver.common.by import By
from last_run import last_run
from price_tracker import (
    initialize_driver,
    load_products,
    save_products,
    save_price_history,
    format_title,
)
from email_sender import send_price_alert
from chart_generator import generate_chart_image
from telegram_sender import send_price_alert_telegram


async def track_prices():
    driver = initialize_driver()
    products = load_products()

    try:
        for product in products:
            try:
                product_id = product["link"].split("/")[-1]
                driver.get(product["link"])

                # Get product details
                title = driver.find_element(By.ID, "productTitle").text
                title = format_title(title)
                product["name"] = title

                # Get current price
                try:
                    price_element = driver.find_element(By.CLASS_NAME, "priceToPay")
                except Exception as e:
                    product["status"] = "Unavailable"
                    print(f"Product {product['name']} is unavailable.")
                    continue

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
                    product["status"] = ""

                    chart_path = generate_chart_image(
                        product_id, title, current_price, new_price
                    )
                    send_price_alert(product, current_price, new_price, chart_path)
                    await send_price_alert_telegram(
                        product, current_price, new_price, chart_path
                    )
                    print(f"Price dropped for {product['name']}")
                elif new_price > current_price:
                    # Price increased - just update
                    save_price_history(product_id, new_price)
                    generate_chart_image(product_id, title, current_price, new_price)
                    product["price"] = new_price
                    product["status"] = ""
                    print(f"Price increased for {product['name']}")
                else:
                    save_price_history(product_id, new_price)
                    print(f"Price unchanged for {product['name']}")

                await asyncio.sleep(random.randint(1, 5))

            except Exception as e:
                # print(
                #     f"Error processing {product.get('name', 'unknown')}:\n{traceback.format_exc()}"
                # )
                print(e)

    finally:
        driver.quit()
        save_products(products)
        last_run()


if __name__ == "__main__":
    asyncio.run(track_prices())
