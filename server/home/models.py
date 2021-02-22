from django.db import models

class HomeData(models.Model):
    username = models.CharField(max_length=100, primary_key=True)
    azure_key = models.CharField(max_length=100)
    azure_end = models.CharField(max_length=100)
    wit_key = models.CharField(max_length=100)
    weather_key = models.CharField(max_length=100)
    bridge_ip = models.CharField(max_length=100)