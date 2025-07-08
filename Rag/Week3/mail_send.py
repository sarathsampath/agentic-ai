import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(recipient_email, subject, body):
    try:
        # Setup MIME
        message = MIMEMultipart()
        message["From"] = "xyz@gmail.com"
        message["To"] = recipient_email
        message["Subject"] = subject

        # Add body
        message.attach(MIMEText(body, "plain"))

        # Connect to Gmail SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Secure the connection
        server.login("xyz@gmail.com", "xyz")

        # Send the email
        server.sendmail("xyz@gmail.com", "abc@gmail.com", message.as_string())
        server.quit()
        print("✅ Email sent successfully!")
        return "Email sent successfully!"

    except Exception as e:
        print("❌ Failed to send email:", e)

