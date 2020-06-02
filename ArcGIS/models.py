from django.db import models

class ElevationPoint(models.Model):
    point_name = models.CharField(max_length=32)
    point_type = models.CharField(max_length=32, null=True)
    section = models.CharField(max_length=32, null=True)
    X = models.FloatField(null=True)
    Y = models.FloatField(null=True)
    Z = models.FloatField(null=True)
    X_touyin = models.FloatField(null=True)
    Y_touyin = models.FloatField(null=True)
    Z_touyin = models.FloatField(null=True)
    coordinates = models.TextField(null=True)

class ElevationPointFile(models.Model):
    file_type = models.CharField(max_length=32, null=True)
    file_name = models.CharField(max_length=32, null=True)
    section = models.CharField(max_length=32, null=True)
    coordinates = models.TextField(null=True)
    shp_file = models.FileField(upload_to='shapefilezip')
