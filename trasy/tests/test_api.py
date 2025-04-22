from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework import status
from editor.models import BackgroundImage, Route, RoutePoint
from django.contrib.auth.models import User
import json

class APITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='apiuser', password='apipassword')
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.bg_image = BackgroundImage.objects.create(image='api_test.jpg', name='API Test Image')
        self.route = Route.objects.create(user=self.user, background=self.bg_image, name='API Test Route')

    def test_api_route_list(self):
        url = reverse('trasa-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_api_route_create(self):
        url = reverse('trasa-list')
        data = {'name': 'API Route 2', 'background': self.bg_image.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Route.objects.filter(name='API Route 2', user=self.user).count(), 1)

    def test_api_route_point_create(self):
        url = reverse('trasa-punkty', args=[self.route.id])
        data = {'order': 1, 'x': 2.0, 'y': 2.0}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RoutePoint.objects.filter(route=self.route, x=2.0, y=2.0).count(), 1)

    def test_api_route_delete(self):
        route_id = self.route.id
        url = reverse('trasa-detail', args=[route_id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Route.objects.filter(id=route_id).exists())

    def test_api_route_point_delete(self):
        route_point = RoutePoint.objects.create(route=self.route, order=1, x=3.0, y=3.0)
        url = reverse('punkt-detail', args=[route_point.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(RoutePoint.objects.filter(id=route_point.id).exists())