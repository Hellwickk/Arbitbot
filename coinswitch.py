from cryptography.hazmat.primitives.asymmetric import ed25519
from urllib.parse import urlparse, urlencode
import urllib
import json
import requests


def place_order(order_type, price, exchange, symbol, quantity):
    print(order_type, price, exchange, symbol, quantity)
    try:
        secret_key = "ac04fa9ddff32ff10f5ced6f9329f3ae62edcbff4e0b55d28d5e3a60436a8aa7"
        api_key = "0dd83597890081d55142dae80504960e0c6ad15ce1640aad4fc85b34546e04a9"
        endpoint = "/trade/api/v2/order"
        method = "POST"

        payload = {
            "side": order_type,
            "symbol": symbol,
            "type": "limit",
            "price": price,
            "quantity": quantity,
            "exchange": exchange
        }

        payload = remove_trailing_zeros(payload)

        unquote_endpoint = endpoint

        signature_msg = method + unquote_endpoint + json.dumps(payload, separators=(',', ':'), sort_keys=True)

        request_string = bytes(signature_msg, 'utf-8')
        secret_key_bytes = bytes.fromhex(secret_key)
        secret_key = ed25519.Ed25519PrivateKey.from_private_bytes(secret_key_bytes)
        signature_bytes = secret_key.sign(request_string)
        signature = signature_bytes.hex()

        url = "https://coinswitch.co" + endpoint

        headers = {
            'Content-Type': 'application/json',
            'X-AUTH-SIGNATURE': signature,
            'X-AUTH-APIKEY': api_key
        }

        response = requests.request("POST", url, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        print(e)
        return {}


def get_depth(params):
    try:
        endpoint = "/trade/api/v2/depth"

        method = "GET"
        payload = {}

        secret_key = "ac04fa9ddff32ff10f5ced6f9329f3ae62edcbff4e0b55d28d5e3a60436a8aa7"
        api_key = "0dd83597890081d55142dae80504960e0c6ad15ce1640aad4fc85b34546e04a9"

        unquote_endpoint = endpoint

        if method == "GET" and len(params) != 0:
            endpoint += ('&', '?')[urlparse(endpoint).query == ''] + urlencode(params)
            unquote_endpoint = urllib.parse.unquote_plus(endpoint)

        signature_msg = method + unquote_endpoint + json.dumps(payload, separators=(',', ':'), sort_keys=True)

        request_string = bytes(signature_msg, 'utf-8')
        secret_key_bytes = bytes.fromhex(secret_key)
        secret_key = ed25519.Ed25519PrivateKey.from_private_bytes(secret_key_bytes)
        signature_bytes = secret_key.sign(request_string)
        signature = signature_bytes.hex()

        url = "https://coinswitch.co" + endpoint

        headers = {
            'Content-Type': 'application/json',
            'X-AUTH-SIGNATURE': signature,
            'X-AUTH-APIKEY': api_key
        }

        res = requests.request("GET", url, headers=headers, json=payload)

        return res.json()
    except Exception as e:
        print(e)
        return


def get_order(order_id):
    try:
        params = {
            "order_id": order_id,
        }
        endpoint = "/trade/api/v2/order"

        method = "GET"
        payload = {}

        secret_key = "ac04fa9ddff32ff10f5ced6f9329f3ae62edcbff4e0b55d28d5e3a60436a8aa7"
        api_key = "0dd83597890081d55142dae80504960e0c6ad15ce1640aad4fc85b34546e04a9"

        unquote_endpoint = endpoint

        if method == "GET" and len(params) != 0:
            endpoint += ('&', '?')[urlparse(endpoint).query == ''] + urlencode(params)
            unquote_endpoint = urllib.parse.unquote_plus(endpoint)

        signature_msg = method + unquote_endpoint + json.dumps(payload, separators=(',', ':'), sort_keys=True)

        request_string = bytes(signature_msg, 'utf-8')
        secret_key_bytes = bytes.fromhex(secret_key)
        secret_key = ed25519.Ed25519PrivateKey.from_private_bytes(secret_key_bytes)
        signature_bytes = secret_key.sign(request_string)
        signature = signature_bytes.hex()

        url = "https://coinswitch.co" + endpoint

        headers = {
            'Content-Type': 'application/json',
            'X-AUTH-SIGNATURE': signature,
            'X-AUTH-APIKEY': api_key
        }

        res = requests.request("GET", url, headers=headers, json=payload)

        return res.json()
    except Exception as e:
        print(e)
        return


def cancel_order(order_id):
    try:
        secret_key = "ac04fa9ddff32ff10f5ced6f9329f3ae62edcbff4e0b55d28d5e3a60436a8aa7"
        api_key = "0dd83597890081d55142dae80504960e0c6ad15ce1640aad4fc85b34546e04a9"
        url = "https://coinswitch.co/trade/api/v2/order"

        payload = {
            "order_id": order_id
        }

        headers = {
            'Content-Type': 'application/json',
            'X-AUTH-SIGNATURE': secret_key,
            'X-AUTH-APIKEY': api_key
        }
        response = requests.request("DELETE", url, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        print(e)
        return {}


def get_active_coins(exchange):
    try:
        params = {
            "exchange": exchange,
        }

        endpoint = "/trade/api/v2/coins"

        method = "GET"
        payload = {}

        secret_key = "ac04fa9ddff32ff10f5ced6f9329f3ae62edcbff4e0b55d28d5e3a60436a8aa7"
        api_key = "0dd83597890081d55142dae80504960e0c6ad15ce1640aad4fc85b34546e04a9"

        unquote_endpoint = endpoint

        if method == "GET" and len(params) != 0:
            endpoint += ('&', '?')[urlparse(endpoint).query == ''] + urlencode(params)
            unquote_endpoint = urllib.parse.unquote_plus(endpoint)

        signature_msg = method + unquote_endpoint + json.dumps(payload, separators=(',', ':'), sort_keys=True)

        request_string = bytes(signature_msg, 'utf-8')
        secret_key_bytes = bytes.fromhex(secret_key)
        secret_key = ed25519.Ed25519PrivateKey.from_private_bytes(secret_key_bytes)
        signature_bytes = secret_key.sign(request_string)
        signature = signature_bytes.hex()

        url = "https://coinswitch.co" + endpoint

        headers = {
            'Content-Type': 'application/json',
            'X-AUTH-SIGNATURE': signature,
            'X-AUTH-APIKEY': api_key
        }

        res = requests.request("GET", url, headers=headers, json=payload)

        return res.json()['data'][exchange]
    except Exception as e:
        print(e)
        return


def get_portfolio():
    try:
        params = {}

        endpoint = "/trade/api/v2/user/portfolio"

        method = "GET"
        payload = {}

        secret_key = "ac04fa9ddff32ff10f5ced6f9329f3ae62edcbff4e0b55d28d5e3a60436a8aa7"
        api_key = "0dd83597890081d55142dae80504960e0c6ad15ce1640aad4fc85b34546e04a9"

        unquote_endpoint = endpoint

        if method == "GET" and len(params) != 0:
            endpoint += ('&', '?')[urlparse(endpoint).query == ''] + urlencode(params)
            unquote_endpoint = urllib.parse.unquote_plus(endpoint)

        signature_msg = method + unquote_endpoint + json.dumps(payload, separators=(',', ':'), sort_keys=True)

        request_string = bytes(signature_msg, 'utf-8')
        secret_key_bytes = bytes.fromhex(secret_key)
        secret_key = ed25519.Ed25519PrivateKey.from_private_bytes(secret_key_bytes)
        signature_bytes = secret_key.sign(request_string)
        signature = signature_bytes.hex()

        url = "https://coinswitch.co" + endpoint

        headers = {
            'Content-Type': 'application/json',
            'X-AUTH-SIGNATURE': signature,
            'X-AUTH-APIKEY': api_key
        }

        res = requests.request("GET", url, headers=headers, json=payload)

        return res.json()
    except Exception as e:
        print(e)
        return


def get_min(price_data):
    ratios = [float(x[0]) for x in price_data]
    min_ratio = min(ratios)
    return min_ratio


def remove_trailing_zeros(dictionary):
    for key, value in dictionary.items():
        if isinstance(value, (int, float)) and dictionary[key] == int(dictionary[key]):
            dictionary[key] = int(dictionary[key])
    return dictionary


def get_max(price_data):
    ratios = [float(x[0]) for x in price_data]
    max_ratio = max(ratios)
    return max_ratio
