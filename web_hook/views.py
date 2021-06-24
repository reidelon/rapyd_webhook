# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import requests

url = 'http://509dce88d136.ngrok.io/payment-web-hook'

@csrf_exempt
@require_http_methods(["POST"])
def index(request):
    web_hook_data = request.POST
    r = requests.post(url, json=web_hook_data)
    if not r.ok:
        import logging
        logging.error('Rapyd code response' + str(r.status_code))
    return HttpResponse("Ok.")
