# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import os
from datetime import datetime
from dotenv import load_dotenv
import json

import hashlib
import base64
import requests
import calendar
import string
from random import *
import hmac

load_dotenv(override=True)


RAPYD_ACCESS_KEY = os.environ["RAPYD_ACCESS_KEY"]
RAPYD_SECRET_KEY = os.environ["RAPYD_SECRET_KEY"]

dev = True

if dev:
    redirect_url = 'https://salmonzon.zaelot.com/payment/'
else:
    redirect_url = 'https://salmonzon.zaelot.com/payment/'

base_url = 'https://sandboxapi.rapyd.net'


def ping(request):
    return HttpResponse("pong")


def rapyd_signature(body, http_method, path):
    # idempotency_key = 'aee984befae64'  # Unique for each 'Create Payment' request.
    idempotency_key = base64.urlsafe_b64encode(
                    hashlib.md5(os.urandom(128)).digest())[:13].decode('utf-8')  # Unique for each 'Create Payment' request.

    # salt: randomly generated for each request.
    min_char = 8
    max_char = 12
    allchar = string.ascii_letters + string.punctuation + string.digits
    salt = "".join(
        choice(allchar) for x in range(randint(min_char, max_char)))

    # Current Unix time.
    d = datetime.utcnow()
    timestamp = calendar.timegm(d.utctimetuple())

    to_sign = http_method + path + salt + str(
        timestamp) + RAPYD_ACCESS_KEY + RAPYD_SECRET_KEY + body

    h = hmac.new(bytes(RAPYD_SECRET_KEY, 'utf-8'), bytes(to_sign, 'utf-8'),
                 hashlib.sha256)

    signature = base64.urlsafe_b64encode(str.encode(h.hexdigest()))

    headers = {
        'access_key': RAPYD_ACCESS_KEY,
        'signature': signature,
        'salt': salt,
        'timestamp': str(timestamp),
        'Content-Type': "application\/json",
        'idempotency': idempotency_key
    }

    return headers

@csrf_exempt
@require_http_methods(["POST"])
def get_rapyd_url_payment(request):
    """
    products format expected
        products = [
            {name: "nilo river", amount: "5.8", image: "http://image1.com", quantity: "2" },
            {name: "amazon river", amount: "3", image: "http://image2.com", quantity: "1"}
        ]
    """

    products_input = json.loads(request.POST.get('products'))
    merchant_reference_id = request.POST.get('merchant_reference_id')
    booking_uuid = request.POST.get('booking_uuid')


    path = '/v1/checkout'  # Portion after the base URL.
    complete_checkout_url = f'{redirect_url}{booking_uuid}'
    error_payment_url = f'{redirect_url}{booking_uuid}'

    checkout_body = {}
    checkout_body['currency'] = 'ISK'
    checkout_body['country'] = 'IS'
    checkout_body['complete_checkout_url'] = complete_checkout_url
    checkout_body['error_payment_url'] = error_payment_url
    checkout_body['cart_items'] = products_input
    checkout_body['merchant_reference_id'] = merchant_reference_id
    total_amount = sum(
        [float(x['amount']) * int(x['quantity']) for x in products_input])
    checkout_body['amount'] = int(
        total_amount) if total_amount % 1 == 0 else total_amount

    body = json.dumps(checkout_body, separators=(',', ':'))

    url = base_url + path
    headers = rapyd_signature(body=body, http_method='post', path=path)

    r = requests.post(url, headers=headers, json=checkout_body)
    if r.ok and r.json()['status']['status'] == 'SUCCESS':
        return JsonResponse(r.json()['data']['redirect_url'], safe=False)
    else:
        import logging
        logging.error(f'Rapyd code response {r.status_code}, \n'
                      f'message {r.json()["status"]["response_code"]}\n'
                      f'message {r.json()["status"]["message"]}\n'
                      f'body for signature {body}\n'
                      f'checkout_body for for rapyd {checkout_body}\n')

