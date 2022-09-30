import datetime
from dataclasses import dataclass
from typing import List

import requests
from secrets.config import zettle_api_key, zettle_client_id
headers = {}

from models import *


def get_token():
    initial_headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    data = f'grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&client_id={zettle_client_id}&assertion={zettle_api_key}'

    response = requests.post('https://oauth.zettle.com/token', headers=initial_headers, data=data)
    token = response.json()["access_token"]
    global headers
    headers = {'Authorization': f"Bearer {token}, "}
    return token


def get_transactions(start_datetime, end_datetime):
    url = f"https://finance.izettle.com/v2/accounts/LIQUID/transactions?start={start_datetime.isoformat()}&end={end_datetime.isoformat()}"
    #url = f"https://finance.izettle.com/v2/accounts/LIQUID/transactions?start=2022-03-01T12:42:10&end=2022-03-01T12:42:10"
    response = requests.get(url, headers=headers)
    data = response.json()
    return data


def get_purchases(changed_since: datetime.datetime):
    #return []
    url = f"https://purchase.izettle.com/purchases/v2?startDate={changed_since.strftime('%Y-%m-%dT%H:%M:%SZ')}"
    #url = f"https://purchase.izettle.com/purchases/v2?startDate=2022-08-24T14:15:22Z"
    #url = f"https://purchase.izettle.com/purchases/v2?startDate=2022-25-08T06:36:02Z"
    url = f"https://purchase.izettle.com/purchases/v2"
    response = requests.get(url, headers=headers)
    data = response.json()
    purchases = []
    for raw_purchase in data["purchases"]:
        products = []
        for raw_product in raw_purchase["products"]:
            for count in range(int(raw_product["quantity"])):
                new_product = ProductPurchased(product_uuid="-1", product_name="", unit_price=raw_product['unitPrice'], details="", complete=False)
                if "name" in raw_product:
                    new_product.product_name = raw_product["name"]
                if 'productUuid' in raw_product:
                    new_product.product_uuid = raw_product['productUuid']
                if "details" in raw_product:
                    new_product.details = raw_product["details"]
                    new_product.details = ""
                if 'variantName' in raw_product:
                    new_product.product_variations = raw_product['variantName']
                if "comment" in raw_product:
                    new_product.comment = raw_product['comment']
                products.append(new_product)
        purchase = Purchase(purchase_uuid=raw_purchase['purchaseUUID'], amount=raw_purchase['amount'], products_purchased=products)
        purchases.append(purchase)
    return purchases


get_token()
#get_transactions(datetime.datetime.now() - datetime.timedelta(days = 380), datetime.datetime.now())
