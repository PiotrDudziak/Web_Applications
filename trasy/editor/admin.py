from django.contrib import admin
from .models import BackgroundImage, Route, RoutePoint
from django.utils.html import format_html
from django.shortcuts import reverse
from django.utils.safestring import mark_safe

@admin.register(BackgroundImage)
class BackgroundImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'image')

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'background', 'route_image_link')

    def route_image_link(self, obj):
        return format_html('<a href="{}">Obraz trasy</a>', obj.get_admin_route_image_url())
    route_image_link.short_description = 'Obraz trasy'

@admin.register(RoutePoint)
class RoutePointAdmin(admin.ModelAdmin):
    list_display = ('id', 'route', 'order', 'x', 'y')

