import logging
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import TELEGRAM_CHAT_ID, TELEGRAM_ACCESS_TOKEN
from price_tracker import load_products, save_products

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """sends a welcome message when the /start command is issued."""
    await update.message.reply_text(
        "Welcome to the Price Tracker Bot! Use /track to start tracking products."
    )


async def add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """adds a new product to producs.csv"""
    if not context.args:
        await update.message.reply_text("please proivde a link after the /add command")
        return

    product_link = context.args[0]
    pattern = r"/(?:dp|gp/product)/([A-Z0-9]{10})"
    match = re.search(pattern, product_link)
    if not match:
        await update.message.reply_text(
            "provided link is not a valid Amazon product link"
        )
        return
    product_id = match.group(1)
    canonical_url = f"https://www.amazon.in/dp/{product_id}"
    products = load_products()

    if any(product["link"] == canonical_url for product in products):
        await update.message.reply_text("this product is already being tracked")
        return

    new_product = {
        "name": "",
        "price": 0,
        "status": "new",
        "important": False,
        "link": canonical_url,
    }

    products.append(new_product)
    save_products(products)

    await update.message.reply_text(f"product {product_id} added successfully!")


async def list_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lists the products currently being tracked."""
    products = load_products()

    if not products:
        await update.message.reply_text("No products are currently being tracked.")
        return

    # Prepare data for a text-based table
    table_data = [["Name", "Price", "Link"]]
    for p in products:
        # Limit name length and create a shorter link for display
        name = (p.get("name") or "N/A")[:25]
        price = f"₹{p.get('price', 'N/A')}"
        product_id = p.get("link", "").split("/")[-1]
        link = f"amzn.in/{product_id}" if product_id else "N/A"
        table_data.append([name, price, link])

    # Calculate column widths for alignment
    col_widths = [max(len(str(cell)) for cell in col) for col in zip(*table_data)]

    # Build the table string
    header = " | ".join(
        [cell.ljust(col_widths[i]) for i, cell in enumerate(table_data[0])]
    )
    separator = "-+-".join(["-" * width for width in col_widths])
    body_rows = []
    for row_data in table_data[1:]:
        row_str = " | ".join(
            [cell.ljust(col_widths[i]) for i, cell in enumerate(row_data)]
        )
        body_rows.append(row_str)
    body = "\n".join(body_rows)

    # Using <pre> for pre-formatted monospaced text which respects spaces
    message = (
        f"<b>Products being tracked:</b>\n<pre>{header}\n{separator}\n{body}</pre>"
    )
    await update.message.reply_text(message, parse_mode="HTML")


def main() -> None:
    """Start the bot."""
    application = ApplicationBuilder().token(TELEGRAM_ACCESS_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_product))

    application.add_handler(CommandHandler("list", list_products))
    application.run_polling()


if __name__ == "__main__":
    main()
