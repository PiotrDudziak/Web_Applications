# notifications/views.py
from django.http import StreamingHttpResponse
from .sse import register, event_stream

def notifications_stream(request):
    q = register()
    response = StreamingHttpResponse(
        event_stream(q),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    return response