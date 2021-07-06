# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Payment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payload_data = models.TextField()
    form_url = models.URLField(null=True, blank=True)
    error = models.TextField(default='', blank=True)

    def __str__(self):
        return self.form_url or ''
