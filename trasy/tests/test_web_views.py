from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from editor.models import BackgroundImage, Route, RoutePoint

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_login_required(self):
        response = self.client.get(reverse('route_list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/')

    def test_login_success(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('route_list'))
        self.assertEqual(response.status_code, 200)

class RouteManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.bg_image = BackgroundImage.objects.create(image='test.jpg', name='Test Image')
        self.route = Route.objects.create(user=self.user, background=self.bg_image, name='Test Route')

    def test_create_route(self):
        response = self.client.post(reverse('route_create'), {'name': 'New Route', 'background': self.bg_image.id})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Route.objects.filter(name='New Route', user=self.user).count(), 1)

    def test_delete_route(self):
        route_id = self.route.id
        response = self.client.post(reverse('route_delete', args=[route_id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Route.objects.filter(id=route_id).exists())

class RoutePointManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.bg_image = BackgroundImage.objects.create(image='test.jpg', name='Test Image')
        self.route = Route.objects.create(user=self.user, background=self.bg_image, name='Test Route')

    def test_add_route_point(self):
        response = self.client.post(reverse('add_point', args=[self.route.id]),
                                     {'order': 1, 'x': 1.0, 'y': 1.0})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(RoutePoint.objects.filter(route=self.route, x=1.0, y=1.0).count(), 1)

    def test_delete_route_point(self):
        route_point = RoutePoint.objects.create(route=self.route, order=1, x=1.0, y=1.0)
        response = self.client.post(reverse('delete_point', args=[self.route.id, route_point.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(RoutePoint.objects.filter(id=route_point.id).exists())