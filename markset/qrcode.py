import pyqrcode
import png
from pyqrcode import QRCode
  
  
# String which represents the QR code
s = "0"
  
# Generate QR code
url = pyqrcode.create(s)

url.png('myqr_low.png', scale = 8)