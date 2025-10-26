import asyncio
import random
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from last_run import save_last_run
from price_tracker import (
    initialize_driver,
    load_products,
    save_products,
    save_price_history,
    format_title,
)
from price_tracker import is_sane_price
from deal_analyzer import analyze_deal
from chart_generator import generate_chart_image
from telegram_sender import send_price_alert_telegram
from utils import is_github_actions
from utils import parse_price_to_int


async def track_prices():
    driver = initialize_driver()
    products = load_products()

    try:
        for product in products:
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

                # Get current price
                try:
                    price_element = driver.find_element(By.CLASS_NAME, "a-price-whole")
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
                    # If current price missing or invalid, treat as 0 so we can initialize
                    current_price = 0

                # Basic sanity check against history and last price
                if not is_sane_price(product_id, new_price):
                    print(
                        f"Suspicious price detected for {product_id}: {new_price}. Skipping update."
                    )
                    product["status"] = "Suspicious"
                    continue

                if new_price < current_price:
                    # Price dropped - save and notify (only if save succeeds)
                    saved = save_price_history(product_id, new_price)
                    if not saved:
                        print(
                            f"Did not save suspicious/invalid drop for {product_id}: {new_price}"
                        )
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
                    # Price increased - just update (only if save succeeds)
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
                        print(
                            f"Did not save suspicious/invalid increase for {product_id}: {new_price}"
                        )
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
