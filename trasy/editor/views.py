from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from .models import BackgroundImage, Route, RoutePoint
from .forms import RouteForm, RoutePointForm
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm
import json
from django.core.paginator import Paginator
from django.core.serializers import serialize
from io import BytesIO
from PIL import Image, ImageDraw
from django.contrib.admin.views.decorators import staff_member_required
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from .serializers import RouteSerializer
from .serializers import RoutePointSerializer
from rest_framework import viewsets, permissions, status


def get_background_image_url(request):
    background_name = request.GET.get('name', None)
    try:
        background_image = BackgroundImage.objects.get(name=background_name)
        image_url = background_image.image.url  # Assuming you have an ImageField named 'image'
        return JsonResponse({'image_url': image_url})
    except BackgroundImage.DoesNotExist:
        return JsonResponse({'image_url': ''})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('route_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


# --- ROUTE VIEWS ---

@login_required
def route_list(request):
    background_images = BackgroundImage.objects.all()
    routes = Route.objects.filter(user=request.user)

    # Pagination
    page_number = request.GET.get('page')
    paginator = Paginator(routes, 5)
    trasy = paginator.get_page(page_number)

    return render(request, 'editor/route_list.html', {'background_images': background_images, 'trasy': trasy})

@login_required
def route_create(request, background_id=None):
    background = None
    if background_id:
        background = get_object_or_404(BackgroundImage, id=background_id)

    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            route = form.save(commit=False)
            route.user = request.user
            if background:
                route.background = background
            else:
                route.background = BackgroundImage.objects.first()
            route.save()
            return redirect('route_detail', route_id=route.id)
    else:
        form = RouteForm()
        if background:
            form.initial['background'] = background

    # ---- Add this block ----
    background_images = BackgroundImage.objects.all()
    background_image_urls = {str(bg.id): bg.image.url for bg in background_images}
    # ---- End block ----

    return render(
        request,
        'editor/route_form.html',
        {
            'form': form,
            'background': background,
            'background_image_urls': background_image_urls,  # pass to template
        }
    )


@login_required
def route_detail(request, route_id):
    route = get_object_or_404(Route, id=route_id, user=request.user)
    # Fetch points ordered by their order field
    points = list(RoutePoint.objects.filter(route=route).order_by('order').values('id', 'x', 'y'))
    point_form = RoutePointForm()
    background_image_url = ''

    if route.background and route.background.image:
        background_image_url = route.background.image.url  # Use relative URL

    context = {
        'route': route,
        'points': points,
        'point_form': point_form,
        'background_image_url': background_image_url,
    }

    return render(request, 'editor/route_detail.html', context)


@login_required
def add_point(request, route_id):
    route = get_object_or_404(Route, id=route_id, user=request.user)
    if request.method == 'POST':
        form = RoutePointForm(request.POST)
        if form.is_valid():
            point = form.save(commit=False)
            point.route = route
            point.order = route.points.count() + 1
            point.save()
    return redirect('route_detail', route_id=route.id)


@login_required
def delete_point(request, route_id, point_id):
    route = get_object_or_404(Route, id=route_id, user=request.user)
    point = get_object_or_404(RoutePoint, id=point_id, route=route)
    point.delete()

    # Reorder the remaining points
    points = RoutePoint.objects.filter(route=route).order_by('order')
    for i, p in enumerate(points):
        p.order = i
        p.save()

    return redirect('route_detail', route_id=route.id)

# --- AJAX views ---
@login_required
@csrf_exempt
def add_point_ajax(request, route_id):
    if request.method == 'POST':
        route = get_object_or_404(Route, id=route_id, user=request.user)
        data = json.loads(request.body.decode('utf-8'))
        x = data.get('x')
        y = data.get('y')

        if x is not None and y is not None:
            point = RoutePoint.objects.create(route=route, x=x, y=y)
            points_data = list(route.points.values('x', 'y'))
            return JsonResponse({'status': 'success', 'points': points_data})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid x or y coordinates'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@login_required
@csrf_exempt
def move_point_ajax(request, route_id):
    if request.method == 'POST':
        route = get_object_or_404(Route, id=route_id, user=request.user)
        d = json.loads(request.body)
        idx, x, y = d['idx'], d['x'], d['y']
        point = route.points.all()[idx]
        point.x = x
        point.y = y
        point.save()
        points = list(route.points.values('x', 'y'))
        return JsonResponse({'points': points})


@login_required
@csrf_exempt
def reorder_points_ajax(request, route_id):
    if request.method == 'POST':
        route = get_object_or_404(Route, id=route_id, user=request.user)
        d = json.loads(request.body)
        order = d['order']
        for new_order, idx in enumerate(order, 1):
            point = route.points.all()[idx]
            point.order = new_order
            point.save()
        points = list(route.points.order_by('order').values('x', 'y'))
        return JsonResponse({'points': points})

@login_required
@csrf_exempt
def save_points_ajax(request, route_id):
    if request.method == 'POST':
        route = get_object_or_404(Route, id=route_id, user=request.user)
        data = json.loads(request.body)
        points_data = data.get('points', [])

        # Fetch existing points to determine the maximum order
        existing_points = list(RoutePoint.objects.filter(route=route).order_by('order'))
        max_order = existing_points[-1].order + 1 if existing_points else 0

        frontend_ids = set()
        for i, point_data in enumerate(points_data):
            point_id = point_data.get('id')
            if point_id:
                point = get_object_or_404(RoutePoint, id=point_id, route=route)
                point.x = point_data['x']
                point.y = point_data['y']
                point.order = i
                point.save()
                frontend_ids.add(point_id)
            else:
                new_point = RoutePoint.objects.create(
                    route=route,
                    x=point_data['x'],
                    y=point_data['y'],
                    order=max_order + i
                )
                frontend_ids.add(new_point.id)

        # Delete DB points not in frontend list
        RoutePoint.objects.filter(route=route).exclude(id__in=frontend_ids).delete()

        # Return updated list
        points = list(RoutePoint.objects.filter(route=route).order_by('order').values('id', 'x', 'y'))
        return JsonResponse({'status': 'success', 'points': points})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# New AJAX view to get points
@login_required
def get_points_ajax(request, route_id):
    route = get_object_or_404(Route, id=route_id, user=request.user)
    points = list(RoutePoint.objects.filter(route=route).order_by('order').values('id', 'x', 'y'))
    return JsonResponse({'points': points})

@staff_member_required
def admin_route_image(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    points = RoutePoint.objects.filter(route=route).order_by('order')

    canvas_width = 1200
    canvas_height = 900

    # Create canvas
    image = Image.new('RGB', (canvas_width, canvas_height), 'white')
    draw = ImageDraw.Draw(image)

    # Draw background image resized to canvas
    if route.background and route.background.image:
        try:
            background_image = Image.open(route.background.image.path).convert('RGB')
            background_image = background_image.resize((canvas_width, canvas_height), Image.LANCZOS)
            image.paste(background_image, (0, 0))
        except Exception as e:
            print("Background paste error:", e)

    route_points = [(int(p.x), int(p.y)) for p in points]

    if len(route_points) > 1:
        draw.line(route_points, fill='red', width=2)
        # Close the route (last point to first)
        draw.line([route_points[-1], route_points[0]], fill='red', width=2)
    for x, y in route_points:
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill='blue')

    buffer = BytesIO()
    image.save(buffer, 'PNG')
    buffer.seek(0)
    return HttpResponse(buffer.read(), content_type='image/png')


class RouteViewSet(viewsets.ModelViewSet):
    serializer_class = RouteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Route.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get', 'post'], url_path='punkty')
    def punkty(self, request, pk=None):
        route = self.get_object()
        if request.method == 'GET':
            points = RoutePoint.objects.filter(route=route).order_by('order')
            return Response(RoutePointSerializer(points, many=True).data)
        elif request.method == 'POST':
            serializer = RoutePointSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(route=route)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RoutePointViewSet(viewsets.ModelViewSet):
    serializer_class = RoutePointSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filtering points by user's routes only
        return RoutePoint.objects.filter(route__user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        point = self.get_object()
        if point.route.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

@login_required
def route_delete(request, route_id):
    route = get_object_or_404(Route, id=route_id, user=request.user)
    route.delete()
    return redirect('route_list')