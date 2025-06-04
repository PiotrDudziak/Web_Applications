# notifications/views.py
from django.http import StreamingHttpResponse
from .sse import register, event_stream

def notifications_stream(request):
    from notifications.sse import register, event_stream
    response = StreamingHttpResponse(
        event_stream(register()),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response