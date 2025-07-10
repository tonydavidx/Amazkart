import os
import pandas as pd
from config import DATA_DIR
from utils import load_and_process_data


def calculate_price_extremes(df: pd.DataFrame) -> tuple[float, str, float, str] | None:
    """Calculates the minimum and maximum prices and their dates from a dataframe."""
    if df.empty:
        return None

    min_price_row = df.loc[df['price'].idxmin()]
    min_price = min_price_row['price']
    min_price_date = min_price_row['datetime'].strftime('%d-%m-%Y')

    max_price_row = df.loc[df['price'].idxmax()]
    max_price = max_price_row['price']
    max_price_date = max_price_row['datetime'].strftime('%d-%m-%Y')

    return min_price, min_price_date, max_price, max_price_date


def analyze_deal(
    product_id: str, new_price: int, old_price: int
) -> tuple[str, str] | None:
    """Analyze the price with historical price data and return a summary"""
    history_file = os.path.join(DATA_DIR, f"{product_id}.csv")

    df = load_and_process_data(history_file)

    if df is None or len(df) < 2:
        return None

    # exclude the last entry as it is the current price
    historical_df = df.iloc[:-1]
    if historical_df.empty:
        return None

    extremes = calculate_price_extremes(historical_df)
    if extremes is None:
        return None
    min_price, min_price_date, max_price, max_price_date = extremes

    avg_price = historical_df["price"].mean()

    if new_price <= min_price:
        return ("🔥", f"Hot deal! This is the lowest price ever. Previous low was ₹{min_price} on {min_price_date}.")

    if new_price < avg_price and ((avg_price - new_price) / avg_price) > 0.15:
        percent_below_avg = (avg_price - new_price) / avg_price * 100
        return ("✅", f"Good deal! {percent_below_avg:.0f}% below average price. The historical price range is ₹{min_price} ({min_price_date}) to ₹{max_price} ({max_price_date}).")

    return None

def get_price_extremes(product_id: str) -> tuple[int, str, int, str] | None:
    """Get the min and max price and their dates for a product."""
    history_file = os.path.join(DATA_DIR, f"{product_id}.csv")

    df = load_and_process_data(history_file)

    if df is None or len(df) < 2:
        return None

    return calculate_price_extremes(df)