import asyncio
import telegram
from config import TELEGRAM_CHAT_ID, TELEGRAM_ACCESS_TOKEN


async def send_price_alert_telegram(
    product_info, old_price, new_price, chart_path=None, deal_analysis=None
):
    """Sends a price drop alert to a Telegram chat."""
    if not TELEGRAM_CHAT_ID or not TELEGRAM_ACCESS_TOKEN:
        print(
            "Telegram token or chat ID not configured. Skipping Telegram notification."
        )
        return

    if new_price >= old_price:
        return

    bot = telegram.Bot(token=TELEGRAM_ACCESS_TOKEN)
    price_drop_percentage = (old_price - new_price) / old_price * 100

    deal_text = ""
    if deal_analysis:
        deal_emoji, deal_message = deal_analysis
        deal_text = f"\n\n{deal_emoji} <b>{deal_message}</b>"

    # Use HTML for rich formatting, similar to the email sender
    message = (
        f"<b>Price Drop Alert! 🚨</b>\n\n"
        f"<b>{product_info['name']}</b>\n\n"
        f"Price dropped from <strike>₹{old_price:,}</strike> to <b>₹{new_price:,}</b>\n"
        f"You're saving: ₹{old_price - new_price:,} ({price_drop_percentage:.1f}%)\n\n"
        f'<a href="{product_info["link"]}">View on Amazon</a>'
        f"{deal_text}\n\n"
    )

    try:
        if chart_path:
            with open(chart_path, "rb") as chart_image:
                await bot.send_photo(
                    chat_id=TELEGRAM_CHAT_ID,
                    photo=chart_image,
                    caption=message,
                    parse_mode=telegram.constants.ParseMode.HTML,
                )
        else:
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=message,
                parse_mode=telegram.constants.ParseMode.HTML,
            )
        print(f"Telegram alert sent for {product_info['name']}.")
    except Exception as e:
        print(f"Failed to send Telegram alert for {product_info['name']}: {e}")


if __name__ == "__main__":
    # Example usage for testing the function directly.
    # To run an async function from the top level, you use asyncio.run().
    test_product = {"name": "Test Product", "link": "https://amazon.in"}
    asyncio.run(send_price_alert_telegram(test_product, 1000, 800))
