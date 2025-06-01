from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from .models import BackgroundImage, Route, RoutePoint
from .forms import RouteForm, RoutePointForm
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm
import json
from django.core.paginator import Paginator
from io import BytesIO
from PIL import Image, ImageDraw
from django.contrib.admin.views.decorators import staff_member_required
from rest_framework.response import Response
from rest_framework.decorators import action
from django.views.decorators.http import require_POST
from .serializers import RouteSerializer
from .serializers import RoutePointSerializer
from rest_framework import viewsets, permissions, status
from .models import BackgroundImage, Route, RoutePoint, GameBoard, Path
from .forms import RouteForm, RoutePointForm, GameBoardForm, PathForm


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
    trasy_qs = Route.objects.filter(user=request.user).order_by('-id')
    plansze_qs = GameBoard.objects.filter(user=request.user).order_by('-id')
    sciezki_qs = Path.objects.filter(user=request.user).order_by('-created_at')

    trasy = Paginator(trasy_qs, 5).get_page(request.GET.get('route_page'))
    plansze = Paginator(plansze_qs, 5).get_page(request.GET.get('board_page'))
    sciezki = Paginator(sciezki_qs, 5).get_page(request.GET.get('path_page'))

    return render(request, 'editor/route_list.html', {
        'trasy': trasy,
        'plansze': plansze,
        'sciezki': sciezki,
    })

@login_required
def route_create(request):
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            route = form.save(commit=False)
            route.user = request.user
            # Pole background jest ustawiane z formularza
            route.save()
            return redirect('route_detail', route_id=route.id)
    else:
        form = RouteForm()

    background_images = BackgroundImage.objects.all()
    background_image_urls = {str(bg.id): bg.image.url for bg in background_images}
    return render(
        request,
        'editor/route_form.html',
        {
            'form': form,
            'background_image_urls': background_image_urls,
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


@login_required
def gameboard_list(request):
    boards = GameBoard.objects.filter(user=request.user).order_by('id')
    plansze = Paginator(boards, 5).get_page(request.GET.get('page'))
    return render(request, 'editor/gameboard_list.html', {'plansze': plansze})



@login_required
def create_or_edit_board(request, board_id=None):
    board = get_object_or_404(GameBoard, id=board_id, user=request.user) if board_id else None
    errors = {}
    colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF']  # Colors for dots

    if request.method == 'GET':
        if board:
            # Editing: render gameboard_detail.html for interactive grid
            return render(request, 'editor/gameboard_detail.html', {
                'board': board,
                'dots': board.dots,
                'colors': colors
            })
        # Creating: render gameboard_form.html with form
        form = GameBoardForm()
        return render(request, 'editor/gameboard_form.html', {
            'form': form,
            'boards': GameBoard.objects.filter(user=request.user),
            'errors': {},
        })

    # Handle POST for creating a new board
    action = request.POST.get('action')
    form = GameBoardForm(request.POST)

    if action == 'create':
        if form.is_valid():
            name = form.cleaned_data['name'].strip()
            rows = form.cleaned_data['rows']
            cols = form.cleaned_data['cols']
            if not name:
                errors['name'] = 'Podaj nazwę planszy'
            if rows < 1 or cols < 1:
                errors['dimensions'] = 'Wymiary muszą być dodatnie'
            if not errors:
                new_board = GameBoard.objects.create(
                    user=request.user,
                    name=name,
                    rows=rows,
                    cols=cols,
                    dots=[]
                )
                return redirect('gameboard_detail', new_board.id)
        else:
            errors.update(form.errors)

    # If errors or invalid form, re-render form
    return render(request, 'editor/gameboard_form.html', {
        'form': form,
        'boards': GameBoard.objects.filter(user=request.user),
        'errors': errors,
    })

@login_required
def delete_board(request, board_id):
    board = get_object_or_404(GameBoard, id=board_id, user=request.user)
    if request.method == 'POST':
        board.delete()
    return redirect('route_list')

@require_POST
def save_board(request, pk):
    data = json.loads(request.body)
    board = get_object_or_404(GameBoard, pk=pk, user=request.user)
    name = data.get('name', board.name).strip()
    rows = data.get('rows', board.rows)
    cols = data.get('cols', board.cols)
    dots = data.get('dots', [])

    if not name:
        return JsonResponse({'error': 'Nazwa planszy jest wymagana'}, status=400)
    if not isinstance(rows, int) or not isinstance(cols, int) or rows < 1 or cols < 1:
        return JsonResponse({'error': 'Nieprawidłowe wymiary'}, status=400)

    # Validate dots
    for dot in dots:
        if not (isinstance(dot.get('row'), int) and isinstance(dot.get('col'), int) and isinstance(dot.get('color'), str)):
            return JsonResponse({'error': 'Nieprawidłowy format kropek'}, status=400)
        if not (0 <= dot['row'] < rows and 0 <= dot['col'] < cols):
            return JsonResponse({'error': 'Kropki poza granicami planszy'}, status=400)

    board.name = name
    board.rows = rows
    board.cols = cols
    board.dots = dots
    board.save()
    return JsonResponse({'board_id': board.pk})


@require_POST
def save_dots_ajax(request, pk):
    board = get_object_or_404(GameBoard, pk=pk)
    data = json.loads(request.body)
    board.dots = data.get('dots', [])
    board.save(update_fields=['dots'])
    return JsonResponse({'status': 'success', 'dots': board.dots})

@login_required
def path_edit(request, board_id, path_id=None):
    board = get_object_or_404(GameBoard, pk=board_id)
    path = get_object_or_404(Path, pk=path_id, user=request.user) if path_id else None
    return render(request, 'editor/path_edit.html', {
        'board': board,
        'path': path,
        'initial': path.path_data if path else [],
    })

@require_POST
@login_required
def path_save(request, board_id, path_id=None):
    data = json.loads(request.body)
    points = data.get('points', [])
    board = get_object_or_404(GameBoard, pk=board_id)
    if path_id:
        p = get_object_or_404(Path, pk=path_id, user=request.user)
        p.path_data = points
    else:
        p = Path(user=request.user, board=board, name=data.get('name',''), path_data=points)
    p.save()
    return JsonResponse({'path_id': p.pk})

@login_required
def path_form(request):
    if request.method == 'POST':
        form = PathForm(request.POST)
        if form.is_valid():
            path = form.save(commit=False)
            path.user = request.user
            path.save()
            return redirect('path_edit', board_id=path.board.id, path_id=path.id)
    else:
        form = PathForm()
    return render(request, 'editor/path_form.html', {'form': form})

def gameboard_preview(request, board_id):
    try:
        board = GameBoard.objects.get(id=board_id)
        data = {
            'rows': board.rows,
            'cols': board.cols,
            'dots': board.dots,
        }
        return JsonResponse(data)
    except GameBoard.DoesNotExist:
        return JsonResponse({'error': 'Plansza nie znaleziona'}, status=404)


@login_required
def path_edit(request, board_id, path_id):
    board = get_object_or_404(GameBoard, id=board_id)
    path = get_object_or_404(Path, id=path_id, board=board)
    points = path.path_data or []
    return render(request, 'editor/path_edit.html', {
        'board': board,
        'path': path,
        'initial': json.dumps(points),
    })

@require_POST
@login_required
def path_save(request, board_id, path_id=None):
    data = json.loads(request.body)
    points = data.get('points', [])

    # usuń duplikaty występujące pod rząd
    cleaned = []
    for p in points:
        if not cleaned or p != cleaned[-1]:
            cleaned.append(p)
    points = cleaned

    board = get_object_or_404(GameBoard, pk=board_id)
    if path_id:
        p = get_object_or_404(Path, pk=path_id, user=request.user)
        p.path_data = points
    else:
        p = Path(user=request.user, board=board, name=data.get('name',''), path_data=points)
    p.line_color = data.get('line_color', getattr(p, 'line_color', None))
    p.save(update_fields=['path_data', 'line_color'])
    return JsonResponse({'path_id': p.pk})

@require_POST
@login_required
def path_delete_point(request, board_id, path_id):
    path = get_object_or_404(Path, id=path_id, board_id=board_id, user=request.user)
    data = json.loads(request.body)
    index = data.get('index')
    if index is not None and 0 <= index < len(path.path_data):
        path.path_data.pop(index)
        path.save(update_fields=['path_data'])
        return JsonResponse({'points': path.path_data})
    return JsonResponse({'error': 'Invalid index'}, status=400)

@require_POST
@login_required
def path_reorder_points(request, board_id, path_id):
    path = get_object_or_404(Path, id=path_id, board_id=board_id, user=request.user)
    data = json.loads(request.body)
    order = data.get('order', [])
    if len(order) == len(path.path_data):
        reordered_points = [path.path_data[i] for i in order]
        path.path_data = reordered_points
        path.save(update_fields=['path_data'])
        return JsonResponse({'points': path.path_data})
    return JsonResponse({'error': 'Invalid order'}, status=400)

@login_required
def path_delete(request, board_id, path_id):
    path = get_object_or_404(Path, id=path_id, board_id=board_id, user=request.user)
    if request.method == 'POST':
        path.delete()
        return redirect('route_list')
    return JsonResponse({'error': 'Invalid request method'}, status=405)

