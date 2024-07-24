from django.db import models

class ImageModel(models.Model):
    name = models.CharField(max_length=255)
    image = models.BinaryField()
    def __str__(self):
        return self.name

class Images(models.Model):
    Detection_Time = models.DateTimeField(auto_now_add=True)
    image_name = models.CharField(max_length=255)
    Pull_Measurement = models.CharField(max_length=255)
    coustomer = models.TextField(max_length=255)
    image_url = models.URLField()

    def __str__(self):
        return f'{self.Detection_Time} : {self.image_name} : {self.Pull_Measurement} :  {self.coustomer} : {self.image_url}'
