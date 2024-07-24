from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import Images


class TestDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = '__all__'


class TestDataSerializer(serializers.ModelSerializer):

    Detection_Time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    # Detection_Time = serializers.DateTimeField(format="%Y-%m-%d")
    class Meta:
        model = Images
        fields = '__all__'
    
