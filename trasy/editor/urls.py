from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from .views import RouteViewSet, RoutePointViewSet
from . import views

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
path('gameboards/', views.gameboard_list, name='gameboard_list'),
    path('gameboards/create/', views.create_or_edit_board, name='gameboard_create'),
    path('gameboards/<int:board_id>/edit/', views.create_or_edit_board, name='gameboard_detail'),
    path('gameboards/<int:board_id>/delete/', views.delete_board, name='gameboard_delete'),
    path('gameboards/create/', views.save_board, name='gameboard_create'),
    path('gameboards/<int:pk>/save/', views.save_board, name='save_board'),
    path('gameboards/<int:pk>/save_dots_ajax/', views.save_dots_ajax, name='gameboard_save_dots_ajax'),
path('boards/<int:board_id>/paths/new/', views.path_edit, name='path_new'),
  path('boards/<int:board_id>/paths/<int:path_id>/edit/', views.path_edit, name='path_edit'),
  path('boards/<int:board_id>/paths/save/', views.path_save, name='path_save_new'),
  path('boards/<int:board_id>/paths/<int:path_id>/save/', views.path_save, name='path_save'),
path('ścieżki/nowa/', views.path_form, name='path_form'),
path('gameboard_preview/<int:board_id>/', views.gameboard_preview, name='gameboard_preview'),
path('boards/<int:board_id>/paths/<int:path_id>/edit/', views.path_edit, name='path_edit'),
    path('boards/<int:board_id>/paths/<int:path_id>/save/', views.path_save, name='path_save'),
path('boards/<int:board_id>/paths/<int:path_id>/delete_point/', views.path_delete_point, name='path_delete_point'),
    path('boards/<int:board_id>/paths/<int:path_id>/reorder_points/', views.path_reorder_points, name='path_reorder_points'),
    path('boards/<int:board_id>/paths/<int:path_id>/delete/', views.path_delete, name='path_delete'),
path('sse/', include('notifications.urls')),

]