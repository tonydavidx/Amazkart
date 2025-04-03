import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import os
from datetime import datetime
from config import DATA_DIR
import time


def generate_chart_image(
    product_id, product_name, current_price, new_price, timeout=30
):
    """
    Generate price history chart image with timeout protection
    Returns: Path to generated image or None if failed
    """
    start_time = time.time()
    history_file = os.path.join(DATA_DIR, f"{product_id}.csv")
    image_path = os.path.join(DATA_DIR, f"{product_id}_chart.png")

    try:
        # Check if history file exists and has data
        if not os.path.exists(history_file) or os.path.getsize(history_file) < 10:
            print(f"No history data for {product_id}, skipping chart generation")
            return None

        # Read data with timeout check
        while time.time() - start_time < timeout:
            try:
                df = pd.read_csv(history_file)
                if len(df) < 1:
                    return None
                break
            except (pd.errors.EmptyDataError, pd.errors.ParserError):
                print(f"Error reading history file for {product_id}")
                return None

        # Process data
        df["datetime"] = pd.to_datetime(
            df["datetime"], format="%d-%m-%Y %H:%M:%S", errors="coerce"
        )
        df = df.dropna(subset=["datetime", "price"])
        df = df.sort_values("datetime")

        if len(df) < 1:
            return None

        # Calculate stats
        min_price = df["price"].min()
        price_drop = (
            ((current_price - new_price) / current_price * 100) if current_price else 0
        )

        # Create simplified figure
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df["datetime"],
                y=df["price"],
                mode="lines+markers",
                line=dict(color="#FF9900", width=2),
                marker=dict(size=6, color="#FF9900"),
                name="Price",
            )
        )

        # Add horizontal lines
        fig.add_hline(
            y=min_price,
            line_dash="dot",
            line_color="red",
            annotation_text=f"Min: ₹{min_price:,}",
            annotation_position="bottom right",
        )

        fig.add_hline(
            y=new_price,
            line_dash="dash",
            line_color="green",
            annotation_text=f"Current: ₹{new_price:,}",
            annotation_position="top right",
        )

        # Simplified layout
        fig.update_layout(
            title=f"{product_name[:50]}<br><sub>Price History</sub>",
            title_x=0.5,
            template="plotly_white",
            margin=dict(l=50, r=50, t=80, b=50),
            height=400,
            width=600,
            showlegend=False,
            xaxis_title="Date",
            yaxis_title="Price (₹)",
        )

        # Save with timeout check
        try:
            pio.write_image(fig, image_path, format="png", engine="kaleido", scale=1)
            return image_path if os.path.exists(image_path) else None
        except Exception as e:
            print(f"Chart save failed for {product_id}: {str(e)}")
            return None

    except Exception as e:
        print(f"Chart generation failed for {product_id}: {str(e)}")
        return None
