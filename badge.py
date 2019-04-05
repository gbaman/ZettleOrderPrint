import qrcode
from PIL import Image, ImageDraw, ImageFont
from time import sleep

import brother_ql
from brother_ql.raster import BrotherQLRaster
from brother_ql.backends.helpers import send
PRINTER_IDENTIFIER = 'usb://0x04f9:0x2028'

def generate_qr_code(URL):
    img = qrcode.make(URL, error_correction=qrcode.constants.ERROR_CORRECT_M)
    return img


def create_label_image(name, order_id, password, eventname, ticket_name):
    if ticket_name.startswith("Parent"):
        ticket_name = "Parent/Guardian"
    qr_code = generate_qr_code(f'https://workshops.niraspberryjam.com/qr/{order_id}/{password}')

    name_font = ImageFont.truetype("arial.ttf", 80)
    jam_font = ImageFont.truetype("arial.ttf", 30)
    qr_font = ImageFont.truetype("arial.ttf", 20)
    img = Image.new('L', (991, 306), color='white')

    d = ImageDraw.Draw(img)
    d.text((20, 120), name, fill="black", font=name_font)
    d.text((20, 20), eventname, fill="black", font=jam_font)
    d.text((20, 60), f"Order ID : {order_id} -- {ticket_name}", fill="black", font=jam_font)
    d.text((20, 250), "Workshops - https://workshops.niraspberryjam.com", fill="black", font=jam_font)
    img.paste(qr_code.resize((270, 270), Image.ANTIALIAS), (720, 0))
    d.text((740, 250), "Scan me with your phone \n to book into workshops!", fill="black", font=qr_font)

    img.save('generated_badge.png')
    sleep(0.1)
    sendToPrinter('generated_badge.png')



def sendToPrinter(path):
    printer = BrotherQLRaster('QL-570')
    print_data = brother_ql.brother_ql_create.convert(printer, [path], '29x90', dither=True, rotate="auto", hq=False)
    send(print_data, PRINTER_IDENTIFIER)
    print_data = None
    