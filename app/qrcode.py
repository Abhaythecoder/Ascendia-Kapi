import pyqrcode
import png

upi_id = "abhay31204@okicici"   
amount = 1000                    
name = "Abhay"                  

# UPI deep link with variables
s = f"upi://pay?pa={upi_id}&pn={name}&am={amount}&cu=INR"
# s = "www.pornhub.com"

# Generate QR code
url = pyqrcode.create(s)

# Save as SVG
url.svg("myqr.svg", scale=8)

# Save as PNG
url.png("myqr.png", scale=6)
