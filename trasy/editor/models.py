from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class BackgroundImage(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nazwa")
    image = models.ImageField(upload_to='backgrounds/', verbose_name="Obraz")

    class Meta:
        verbose_name = "Obraz tła"
        verbose_name_plural = "Obrazy tła"

    def __str__(self):
        return self.name

class Route(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Użytkownik")
    name = models.CharField(max_length=100, verbose_name="Nazwa")
    background = models.ForeignKey(BackgroundImage, on_delete=models.CASCADE, verbose_name="Tło")

    class Meta:
        verbose_name = "Trasa"
        verbose_name_plural = "Trasy"

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    def get_admin_route_image_url(self):
        return reverse('admin_route_image', args=[self.id])

    class Meta:
        verbose_name = "Trasa"
        verbose_name_plural = "Trasy"

class RoutePoint(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='points', verbose_name="Trasa")
    order = models.PositiveIntegerField(verbose_name="Kolejność")
    x = models.PositiveIntegerField(verbose_name="X")
    y = models.PositiveIntegerField(verbose_name="Y")

    class Meta:
        ordering = ['order']
        verbose_name = "Punkt trasy"
        verbose_name_plural = "Punkty trasy"

    def __str__(self):
        return f"({self.x}, {self.y}) in {self.route.name} - {self.order}"

# Do przytrzymania informacji o kropkach na planszy
class GameBoard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    rows = models.IntegerField()
    cols = models.IntegerField()
    dots = models.JSONField(default=list)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Plansza"
        verbose_name_plural = "Plansze"

class Path(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    board = models.ForeignKey(GameBoard, on_delete=models.CASCADE, related_name='paths')
    name = models.CharField(max_length=100, default="Unnamed Path")
    path_data = models.JSONField(default=list)
    line_color = models.CharField(max_length=7, default='#ff0000', verbose_name="Kolor linii")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        cleaned = []
        for point in self.path_data:
            if not cleaned or point != cleaned[-1]:
                cleaned.append(point)
        self.path_data = cleaned
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Path '{self.name}' for {self.board.name} by {self.user.username}"

    class Meta:
        ordering = ['created_at']
        verbose_name = "Ścieżka"
        verbose_name_plural = "Ścieżki"