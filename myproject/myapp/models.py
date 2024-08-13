from django.db import models

class ImageModel(models.Model):
    name = models.CharField(max_length=255)
    image = models.BinaryField()
    def __str__(self):
        return self.name


class Images(models.Model):
    Detection_Time = models.DateTimeField(auto_now_add=True)
    image_name = models.CharField(max_length=255, null=True, blank=True)
    defect_types = models.CharField(max_length=255, null=True, blank=True)
    Pull_Measurement = models.CharField(max_length=255, default="Steel 10*5°4, 1000.RPM")
    image_url = models.URLField(max_length=255, null=True, blank=True)  # Correct way to store image paths
    classification = models.CharField(max_length=50, default='ok_front')
    timestamp = models.DateTimeField(auto_now=True)
    category = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.Detection_Time} : {self.image_name}: {self.defect_types} : {self.Pull_Measurement} : {self.customer} : {self.image_url} : {self.classification} : {self.timestamp} : {self.category}'
