# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Payment


class PaymentAdmin(admin.ModelAdmin):
    readonly_fields = ('updated_at', 'created_at')
    list_display = ('form_url', 'created_at', 'updated_at')


admin.site.register(Payment, PaymentAdmin)
