from django.test import TestCase
from django.contrib.auth import get_user_model
from editor.models import BackgroundImage, Route, RoutePoint

User = get_user_model()

class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.bg_image = BackgroundImage.objects.create(image='test.jpg', name='Test Image')

    def test_user_creation(self):
        self.assertEqual(User.objects.count(), 1)

    def test_backgroundimage_creation(self):
        self.assertEqual(BackgroundImage.objects.count(), 1)

    def test_create_route(self):
        route = Route.objects.create(user=self.user, background=self.bg_image, name='Test Route')
        self.assertEqual(route.name, 'Test Route')
        self.assertEqual(route.user, self.user)
        self.assertEqual(route.background, self.bg_image)

    def test_route_user_relation(self):
        route = Route.objects.create(user=self.user, background=self.bg_image, name='Test Route')
        self.assertIn(route, self.user.route_set.all())