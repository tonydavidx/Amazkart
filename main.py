import asyncio
import random
import httpx
from bs4 import BeautifulSoup
from last_run import last_run
from price_tracker import (
    load_products,
    save_products,
    save_price_history,
    format_title,
)
from email_sender import send_price_alert
from chart_generator import generate_chart_image
from telegram_sender import send_price_alert_telegram


# Headers to mimic a real browser visit
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "DNT": "1",
}


async def track_prices():
    products = load_products()

    async with httpx.AsyncClient(
        headers=HEADERS, follow_redirects=True, timeout=20.0
    ) as client:
        for product in products:
            try:
                product_id = product["link"].split("/")[-1]
                print(f"Checking price for: {product.get('name') or product_id}")
                response = await client.get(product["link"])
                response.raise_for_status()  # Raise an exception for bad status codes

                soup = BeautifulSoup(response.text, "html.parser")

                # Get product details
                title_element = soup.select_one("span#productTitle")
                if not title_element:
                    print(
                        f"Could not find title for {product_id}. Page might be a captcha or different layout."
                    )
                    continue

                title = format_title(title_element.get_text(strip=True))
                product["name"] = title

                # Get current price
                price_element = soup.select_one(".a-price-whole")
                if not price_element:
                    product["status"] = "Unavailable"
                    print(f"Product {product['name']} is unavailable.")
                    continue

                new_price = int(
                    price_element.get_text(strip=True).replace(",", "").replace(".", "")
                )
                current_price = int(product["price"])

                if new_price < current_price:
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
                    print(f"Price dropped for {product['name']} to {new_price}")
                elif new_price > current_price:
                    # Price increased - just update
                    save_price_history(product_id, new_price)
                    generate_chart_image(product_id, title, current_price, new_price)
                    product["price"] = new_price
                    product["status"] = ""
                    print(f"Price increased for {product['name']} to {new_price}")
                else:
                    print(f"Price unchanged for {product['name']}")

                await asyncio.sleep(random.randint(2, 6))  # Be a good citizen

            except httpx.HTTPStatusError as e:
                print(
                    f"HTTP error for {product.get('name', product_id)}: {e.response.status_code} - {e}"
                )
            except Exception as e:
                print(f"Error processing {product.get('name', product_id)}: {e}")

    save_products(products)
    last_run()


if __name__ == "__main__":
    asyncio.run(track_prices())
    print("Price tracking completed.")
