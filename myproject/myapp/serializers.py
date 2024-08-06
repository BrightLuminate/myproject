from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import Images


class TestDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = '__all__'


class TestDataSerializer(serializers.ModelSerializer):

    Detection_Time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    # Detection_Time = serializers.DateTimeField(format="%H:%M:%S")
    class Meta:
        model = Images
        fields = '__all__'

    def get_image_url(self, obj):
        return obj.image.url
    

class MyAppImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = '__all__'
