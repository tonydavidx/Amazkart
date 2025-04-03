import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from config import EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD


def send_price_alert(product_info, old_price, new_price, chart_path=None):
    print(f"Sending email alert for {product_info['name']}...")
    if new_price >= old_price:
        return

    message = MIMEMultipart()
    message["Subject"] = f"🤖 Price drop for {product_info['name'][:30]}"
    message["From"] = EMAIL_FROM
    message["To"] = EMAIL_TO

    # Email body
    body = f"""
    <html>
        <body>
            <h2>Price Drop Alert! 🚨</h2>
            <h3>{product_info["name"]}</h3>
            <p>Price dropped from <span style="text-decoration: line-through;">₹{old_price:,}</span> 
               to <span style="color: green; font-weight: bold;">₹{new_price:,}</span></p>
            <p>You're saving: ₹{old_price - new_price:,} ({(old_price - new_price) / old_price * 100:.1f}%)</p>
            <p>Link: <a href="{product_info["link"]}">View on Amazon</a></p>
            {f'<img src="cid:price_chart" width="600">' if chart_path else ""}
        </body>
    </html>
    """

    message.attach(MIMEText(body, "html"))

    # Attach chart if available
    if chart_path:
        with open(chart_path, "rb") as img_file:
            img = MIMEImage(img_file.read())
            img.add_header("Content-ID", "<price_chart>")
            message.attach(img)

    # Send email
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_FROM, EMAIL_PASSWORD)
        smtp.send_message(message)
