from PIL import Image, ImageDraw
import sys

img_path = "/Users/mrlaoliai/Desktop/wechat_ocr_debug.png"
out_path = "/Users/mrlaoliai/Desktop/wechat_ocr_debug_dot.png"

try:
    img = Image.open(img_path)
    draw = ImageDraw.Draw(img)
    
    # Coordinates in logical space vs physical space
    # The OCR returned X=71, Y=155 AFTER dividing by 2.
    # This means the Swift script found it at X=142, Y=310 in the image.
    # Wait, let's draw at X=142, Y=310 in the image!
    x, y = 142, 310
    
    r = 10
    draw.ellipse((x-r, y-r, x+r, y+r), fill="red", outline="red")
    
    img.save(out_path)
    print("Saved dot image to desktop!")
except Exception as e:
    print(f"Error: {e}")
