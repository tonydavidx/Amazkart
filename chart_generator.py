import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import os
from datetime import datetime
from config import DATA_DIR
import time
import plotly.subplots as sp


def generate_chart_image(
    product_id, product_name, current_price, new_price, timeout=30
):
    """
    Generate price history chart image with statistics summary
    Returns: Path to generated image or None if failed
    """
    start_time = time.time()
    history_file = os.path.join(DATA_DIR, f"{product_id}.csv")
    image_path = os.path.join(DATA_DIR, f"{product_name}_chart.png")

    try:
        # Check if history file exists and has data
        if not os.path.exists(history_file) or os.path.getsize(history_file) < 10:
            print(f"No history data for {product_id}, skipping chart generation")
            return None

        # Read data
        df = pd.read_csv(history_file)
        if len(df) < 1:
            return None

        # Process data
        df = df[df["price"] != "UNAVAILABLE"]  # Filter out unavailable entries
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df["datetime"] = pd.to_datetime(
            df["datetime"], format="%d-%m-%Y %H:%M:%S", errors="coerce"
        )
        df = df.dropna(subset=["datetime", "price"])
        df = df.sort_values("datetime")

        if len(df) < 1:
            return None

        # Calculate stats
        min_price = df["price"].min()
        max_price = df["price"].max()
        avg_price = df["price"].mean()
        price_drop = (
            ((current_price - new_price) / current_price * 100) if current_price else 0
        )

        # Create figure with subplots
        fig = sp.make_subplots(
            rows=2,
            cols=1,
            row_heights=[0.85, 0.15],
            vertical_spacing=0.05,
            specs=[[{"type": "scatter"}], [{"type": "table"}]],
        )

        # Price line chart
        fig.add_trace(
            go.Scatter(
                x=df["datetime"],
                y=df["price"],
                mode="lines+markers",
                line=dict(color="#FF9900", width=2),
                marker=dict(size=6, color="#FF9900"),
                name="Price",
                hovertemplate="%{y:,.0f}<extra></extra>",
            ),
            row=1,
            col=1,
        )

        # Add horizontal lines
        fig.add_hline(
            y=min_price,
            line_dash="dot",
            line_color="red",
            annotation_text=f"Min: ₹{min_price:,.0f}",
            annotation_position="bottom right",
            row=1,
            col=1,
        )

        fig.add_hline(
            y=new_price,
            line_dash="dash",
            line_color="green",
            annotation_text=f"Current: ₹{new_price:,.0f}",
            annotation_position="top right",
            row=1,
            col=1,
        )

        # Add statistics table
        stats_table = go.Table(
            header=dict(
                values=["Average Price", "Highest Price", "Lowest Price"],
                font=dict(size=12, color="white"),
                fill_color="#232F3E",
                align="center",
            ),
            cells=dict(
                values=[
                    [f"₹{avg_price:,.0f}"],
                    [f"₹{max_price:,.0f}"],
                    [f"₹{min_price:,.0f}"],
                ],
                font=dict(size=14),
                align="center",
            ),
            columnwidth=[1, 1, 1],
        )

        fig.add_trace(stats_table, row=2, col=1)

        # Update layout
        fig.update_layout(
            title=f"<b>{product_name[:50]}</b><br><sub>Price History (Current: ₹{new_price:,.0f})</sub>",
            title_x=0.5,
            template="plotly_white",
            height=600,
            width=800,
            margin=dict(t=100, b=20, l=50, r=50),
            showlegend=False,
            xaxis_rangeslider_visible=False,
        )

        # Update axes
        fig.update_yaxes(title_text="Price (₹)", row=1, col=1)
        fig.update_xaxes(title_text="Date", row=1, col=1)

        # Save image
        pio.write_image(fig, image_path, format="png", engine="kaleido", scale=1)
        return image_path if os.path.exists(image_path) else None

    except Exception as e:
        print(f"Chart generation failed for {product_id}: {str(e)}")
        return None
