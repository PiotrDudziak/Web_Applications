from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from .views import RouteViewSet, RoutePointViewSet

router = DefaultRouter()
router.register(r'trasy', RouteViewSet, basename='trasa')
router.register(r'punkty', RoutePointViewSet, basename='punkt')

urlpatterns = [
    path('get_background_image_url/', views.get_background_image_url, name='get_background_image_url'),
    path('', views.route_list, name='route_list'),
    path('route/create/', views.route_create, name='route_create'),
    path('route/create/<int:background_id>/', views.route_create, name='route_create'),
    path('route/<int:route_id>/', views.route_detail, name='route_detail'),
    path('route/<int:route_id>/add_point/', views.add_point, name='add_point'),
    path('route/<int:route_id>/delete_point/<int:point_id>/', views.delete_point, name='delete_point'),
    path('route/<int:route_id>/add_point_ajax/', views.add_point_ajax, name='add_point_ajax'),
    path('route/<int:route_id>/move_point_ajax/', views.move_point_ajax, name='move_point_ajax'),
    path('route/<int:route_id>/reorder_points_ajax/', views.reorder_points_ajax, name='reorder_points_ajax'),
    path('route/<int:route_id>/save_points_ajax/', views.save_points_ajax, name='save_points_ajax'), # new url
    path('route/<int:route_id>/get_points_ajax/', views.get_points_ajax, name='get_points_ajax'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('route/<int:route_id>/admin_route_image/', views.admin_route_image, name='admin_route_image'),
    path('api/', include(router.urls)),
    path('route/<int:route_id>/delete/', views.route_delete, name='route_delete'),
    path('api/trasy/<int:route_id>/punkty/<int:pk>/', RoutePointViewSet.as_view({'delete': 'destroy'})),
]