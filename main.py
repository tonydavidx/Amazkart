import asyncio
import random
from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from chart_generator import generate_chart_image
from deal_analyzer import analyze_deal
from last_run import save_last_run
from price_tracker import (
    format_title,
    initialize_driver,
    load_products,
    save_price_history,
    save_products,
)
from telegram_sender import send_price_alert_telegram
from utils import is_github_actions, parse_price_to_int


async def track_prices(filter_id=None):
    driver = initialize_driver()
    products = load_products()

    def matches(product):
        if filter_id is None:
            return True
        try:
            idx = int(filter_id)
            return 0 <= idx < len(products) and products[idx] is product
        except ValueError:
            return filter_id in product.get("link", "")

    if filter_id is not None:
        found = any(matches(p) for p in products)
        if not found:
            try:
                int(filter_id)
                print(f"Invalid index: {filter_id}")
            except ValueError:
                print(f"No product found with ASIN: {filter_id}")
            return

    try:
        for product in products:
            if not matches(product):
                continue
            try:
                product_id = product["link"].split("/")[-1]
                # skip unimportant products if run on github actions
                not_important = (
                    product["important"] == "False" or product["important"] == "false"
                )
                if is_github_actions() and not_important:
                    print(
                        f"Skipping {product.get('name', product_id)} for not important"
                    )
                    continue

                print(f"🔍 Checking price for: {product.get('name') or product_id}")
                driver.get(product["link"])

                # Get product details
                try:
                    title_element = driver.find_element(By.ID, "productTitle")
                except NoSuchElementException:
                    print(
                        f"⚠️ Could not find title for {product_id}. Page might be a captcha or different layout."
                    )
                    continue

                title = format_title(title_element.text)
                product["name"] = title

                product_box = driver.find_element(By.ID, "centerCol")
                sleep(3)  # Random sleep to mimic human behavior

                # Get current price
                try:
                    price_element = product_box.find_element(
                        By.CLASS_NAME, "a-price-whole"
                    )
                    print(f"Price: {price_element.text}")
                except NoSuchElementException:
                    product["status"] = "Unavailable"
                    print(f"Product {product['name']} is unavailable.")
                    continue

                # Parse price robustly (handles commas and decimals)
                parsed = parse_price_to_int(price_element.text)
                if parsed is None:
                    product["status"] = "Unavailable"
                    print(
                        f"Could not parse price for {product.get('name', product_id)}. Skipping."
                    )
                    continue
                new_price = parsed

                try:
                    current_price = int(product["price"])
                except Exception:
                    current_price = 0

                # 1. Sanity Check First
                # if not is_sane_price(product_id, new_price):
                #     print(
                #         f"Suspicious price detected for {product_id}: {new_price}. Skipping update."
                #     )
                #     product["status"] = "Suspicious"
                #     continue

                # 2. Handle Price Changes or Initialization
                if current_price == 0:
                    # Initial price fetch
                    saved = save_price_history(product_id, new_price)
                    if saved:
                        product["price"] = new_price
                        product["status"] = ""
                        print(
                            f"✅ Initialized price for {product['name']} to {new_price}"
                        )
                    else:
                        product["status"] = "Suspicious"

                elif new_price < current_price:
                    # Price dropped - save and notify
                    saved = save_price_history(product_id, new_price)
                    if not saved:
                        product["status"] = "Suspicious"
                    else:
                        product["price"] = new_price
                        product["status"] = ""

                        deal_analysis = analyze_deal(
                            product_id, new_price, current_price
                        )

                        chart_path = generate_chart_image(
                            product_id, title, current_price, new_price
                        )
                        await send_price_alert_telegram(
                            product, current_price, new_price, chart_path, deal_analysis
                        )
                        print(f"🤑 Price dropped for {product['name']} to {new_price}")

                elif new_price > current_price:
                    # Price increased - just update
                    saved = save_price_history(product_id, new_price)
                    if saved:
                        generate_chart_image(
                            product_id, title, current_price, new_price
                        )
                        product["price"] = new_price
                        product["status"] = ""
                        print(
                            f"🥲 Price increased for {product['name']} to {new_price}"
                        )
                    else:
                        product["status"] = "Suspicious"
                else:
                    print(f"🙂 Price unchanged for {product['name']}")

                await asyncio.sleep(random.randint(2, 6))  # Be a good citizen

            except Exception as e:
                print(f"Error processing {product.get('name', product_id)}: {e}")

    finally:
        driver.quit()
        save_products(products)
        save_last_run()


if __name__ == "__main__":
    asyncio.run(track_prices())
    print("Price tracking completed.")
