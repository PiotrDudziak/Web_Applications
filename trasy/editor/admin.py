from django.contrib import admin
from .models import BackgroundImage, Route, RoutePoint, GameBoard, Path
from django.utils.html import format_html

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

class PathInline(admin.TabularInline):
    model = Path
    extra = 0
    readonly_fields = ('path_data', 'created_at')
    fields = ('name', 'path_data', 'created_at')
    show_change_link = True

@admin.register(GameBoard)
class GameBoardAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'rows', 'cols')
    inlines = [PathInline]

@admin.register(Path)
class PathAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'board', 'created_at')
    readonly_fields = ('created_at',)