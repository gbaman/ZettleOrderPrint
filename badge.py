import datetime
import time

from PIL import Image, ImageDraw, ImageFont

import brother_ql
from brother_ql.raster import BrotherQLRaster
from brother_ql.backends.helpers import send
import models
import os


PRINTER_IDENTIFIER = 'usb://0x04f9:0x2028'


def create_label_image(purchase: models.Purchase):
    for outer_prodict_id, outer_product in enumerate(purchase.products_purchased):
        img = Image.new('L', (696, 300 + (130*len(purchase.products_purchased))), color='white')
        d = ImageDraw.Draw(img)
        main_font = ImageFont.truetype("arial.ttf", 40)
        d.text((10, 10), "Grant's Pizza", fill="black", font=ImageFont.truetype("arial.ttf", 80, ))
        d.text((10, 120), f"Time: {datetime.datetime.now().strftime('%H:%M:%S')}", fill="black", font=main_font)
        d.text((10, 170), f"Order ID: {purchase.purchase_id}", fill="black", font=main_font)
        d.line((0, 230, img.size[0], 230), fill="black", width=7)
        for product_id, product in enumerate(purchase.products_purchased):
            if outer_prodict_id == product_id:
                d.rectangle((5, 250 + (product_id * 140), img.size[0] - 5, 380 + (product_id * 140)), outline="black", width=10)

            d.text((20, 260 + (product_id * 140)), f"- {product.product_name}", fill="black", font=main_font)
            if product.product_variations:
                d.text((40, 300 + (product_id * 140)), f"{product.clean_product_variations}", fill="black", font=ImageFont.truetype("arial.ttf", 30))
            if product.comment:
                d.text((40, 330 + (product_id * 140)), f"[ {product.comment} ]", fill="black", font=ImageFont.truetype("arial.ttf", 30))
        img.save('generated_badge.png')

        time.sleep(0.5)
        os.startfile('generated_badge.png')
        print()
        send_to_printer(img)
    return


def send_to_printer(path):
    printer = BrotherQLRaster('QL-570')
    print_data = brother_ql.brother_ql_create.convert(printer, [path], '62', dither=True, rotate="auto", hq=False)
    send(print_data, PRINTER_IDENTIFIER)