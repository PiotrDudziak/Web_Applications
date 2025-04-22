# plik: editor/serializers.py
from rest_framework import serializers
from .models import Route, RoutePoint

class RoutePointSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutePoint
        fields = ['id', 'x', 'y', 'order']

class RouteSerializer(serializers.ModelSerializer):
    points = RoutePointSerializer(many=True, read_only=True)

    class Meta:
        model = Route
        fields = ['id', 'name', 'background', 'points']