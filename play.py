import os
from chart_generator import generate_chart_image
from config import DATA_DIR


def create_mock_data():
    """Creates a mock CSV file for testing chart generation."""
    mock_product_id = "MOCK_PRODUCT_123"
    mock_data_file = os.path.join(DATA_DIR, f"{mock_product_id}.csv")

    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    # Mock data with header
    data = [
        ("datetime", "price"),
        ("01-05-2024 10:00:00", "1500"),
        ("02-05-2024 12:30:00", "1450"),
        ("03-05-2024 09:00:00", "1480"),
        ("04-05-2024 00:00:00", "1480"),  # same price, new day
        ("05-05-2024 18:45:00", "1300"),  # big drop
        ("06-05-2024 11:00:00", "1350"),
    ]

    with open(mock_data_file, "w", newline="") as f:
        for row in data:
            f.write(",".join(row) + "\n")

    print(f"Mock data created at: {mock_data_file}")
    return mock_product_id


def test_chart_generation():
    """Tests the chart generation with mock data."""
    # 1. Create mock data
    product_id = create_mock_data()

    # 2. Define mock product info
    product_name = "Mock Product for Chart Testing"
    current_price = 1480  # An older price from before the drop
    new_price = 1300  # The new price we are alerting on

    # 3. Generate the chart
    print("Generating chart...")
    image_path = generate_chart_image(
        product_id, product_name, current_price, new_price
    )

    if image_path:
        print(f"Chart successfully generated and saved to: {image_path}")
    else:
        print("Chart generation failed.")


if __name__ == "__main__":
    test_chart_generation()
