import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import os
from config import DATA_DIR
import plotly.subplots as sp


def _load_and_process_data(history_file):
    """Loads and preprocesses the price history data from a CSV file."""
    if not os.path.exists(history_file) or os.path.getsize(history_file) < 10:
        print(
            f"No history data in {os.path.basename(history_file)}, skipping chart generation."
        )
        return None

    df = pd.read_csv(history_file)
    if df.empty:
        return None

    df = df[df["price"] != "UNAVAILABLE"]
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["datetime"] = pd.to_datetime(
        df["datetime"], format="%d-%m-%Y %H:%M:%S", errors="coerce"
    )
    df = df.dropna(subset=["datetime", "price"])
    df = df.sort_values("datetime")

    return df if not df.empty else None


def _create_chart_title(product_name, old_price, new_price):
    """Creates a dynamic chart title based on the price change."""
    title_line_1 = f"<b>{product_name[:50]}</b>"

    if new_price < old_price:
        price_drop_percent = (old_price - new_price) / old_price * 100
        title_line_2 = f"<sub>Price Drop: <span style='text-decoration: line-through;'>₹{old_price:,.0f}</span> → <b style='color:green;'>₹{new_price:,.0f}</b> ({price_drop_percent:.1f}% off)</sub>"
    elif new_price > old_price:
        title_line_2 = f"<sub>Price Increase: <span style='text-decoration: line-through;'>₹{old_price:,.0f}</span> → <b style='color:red;'>₹{new_price:,.0f}</b></sub>"
    else:
        title_line_2 = f"<sub>Price History (Current: ₹{new_price:,.0f})</sub>"

    return f"{title_line_1}<br>{title_line_2}"


def generate_chart_image(product_id, product_name, old_price, new_price):
    """
    Generate price history chart image with statistics summary
    Returns: Path to generated image or None if failed
    """
    history_file = os.path.join(DATA_DIR, f"{product_id}.csv")
    safe_product_name = "".join(
        c for c in product_name if c.isalnum() or c in (" ", "_")
    ).rstrip()
    image_path = os.path.join(DATA_DIR, f"{safe_product_name}_chart.png")

    try:
        df = _load_and_process_data(history_file)
        if df is None:
            return None

        # Calculate stats
        min_price_row = df.loc[df["price"].idxmin()]
        min_price = min_price_row["price"]
        min_price_date = min_price_row["datetime"].strftime("%d-%b-%Y")
        max_price = df["price"].max()
        avg_price = df["price"].mean()

        # Create figure with subplots
        fig = sp.make_subplots(
            rows=2,
            cols=1,
            row_heights=[0.8, 0.2],
            vertical_spacing=0.1,
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
                hovertemplate="<b>%{x|%d-%b-%Y}</b><br>Price: ₹%{y:,.0f}<extra></extra>",
            ),
            row=1,
            col=1,
        )

        # Add horizontal lines
        fig.add_hline(
            y=min_price,
            line_dash="dot",
            line_color="red",
            annotation_text=f"All-Time Low: ₹{min_price:,.0f}",
            annotation_position="bottom right",
            row=1,
            col=1,
        )

        # Add line for old price if it's different from new price and not the max/min
        if old_price != new_price and old_price not in [min_price, max_price]:
            fig.add_hline(
                y=old_price,
                line_dash="dot",
                line_color="grey",
                annotation_text=f"Old Price: ₹{old_price:,.0f}",
                annotation_position="top left",
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
                values=[
                    "Average Price",
                    "Highest Price",
                    "Lowest Price",
                    "Lowest Price Date",
                ],
                font=dict(size=12, color="white"),
                fill_color="#232F3E",
                align="center",
            ),
            cells=dict(
                values=[
                    f"₹{avg_price:,.0f}",
                    f"₹{max_price:,.0f}",
                    f"₹{min_price:,.0f}",
                    min_price_date,
                ],
                font=dict(size=14),
                align="center",
                height=30,
            ),
        )

        fig.add_trace(stats_table, row=2, col=1)

        # Update layout
        chart_title = _create_chart_title(product_name, old_price, new_price)
        fig.update_layout(
            title=chart_title,
            title_x=0.5,
            template="plotly_white",
            height=650,
            width=800,
            margin=dict(t=100, b=20, l=60, r=60),
            showlegend=False,
            xaxis_rangeslider_visible=False,
            plot_bgcolor="white",
            xaxis=dict(showline=True, linewidth=1, linecolor="lightgrey", mirror=True),
            yaxis=dict(showline=True, linewidth=1, linecolor="lightgrey", mirror=True),
        )

        # Update axes
        fig.update_yaxes(title_text="Price (₹)", row=1, col=1)
        fig.update_xaxes(title_text=None, row=1, col=1)  # "Date" is obvious from ticks

        # Save image
        pio.write_image(fig, image_path, format="png", engine="kaleido", scale=1.2)
        return image_path if os.path.exists(image_path) else None

    except Exception as e:
        print(f"Chart generation failed for {product_id}: {str(e)}")
        return None
