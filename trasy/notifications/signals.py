# notifications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver

from .sse import push_event
from editor.models import GameBoard, Path

@receiver(post_save, sender=GameBoard)
def send_new_board_event(sender, instance, created, **kwargs):
    if created:
        data = {
            "board_id": instance.id,
            "board_name": instance.name,
            "creator_username": instance.user.username
        }
        push_event("newBoard", data)

@receiver(post_save, sender=Path)
def send_new_path_event(sender, instance, created, **kwargs):
    if created:
        data = {
            "path_id": instance.id,
            "board_id": instance.board.id,
            "board_name": instance.board.name,
            "user_username": instance.user.username
        }
        push_event("newPath", data)