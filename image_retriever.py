from PIL import Image
import base64
import io

def make_image(driver, image_name):
    canvas = driver.find_element("tag name", "canvas")

    data = driver.execute_script("""
        var canvas = arguments[0];
        return canvas.toDataURL('image/png').substring(22);
    """, canvas)

    img_bytes = base64.b64decode(data)
    img = Image.open(io.BytesIO(img_bytes))

    img.save(f"{image_name}.png")
