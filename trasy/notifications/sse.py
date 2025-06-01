# notifications/sse.py
import json
import time
from queue import Queue
from threading import Lock

SUBSCRIBERS = []
LOCK = Lock()

def register():
    q = Queue()
    with LOCK:
        SUBSCRIBERS.append(q)
    return q

def unregister(q):
    with LOCK:
        if q in SUBSCRIBERS:
            SUBSCRIBERS.remove(q)

def push_event(event_type, data):
    payload = f"event: {event_type}\n" \
              f"data: {json.dumps(data)}\n\n"
    with LOCK:
        for q in list(SUBSCRIBERS):
            q.put(payload)

def event_stream(q):
    try:
        while True:
            try:
                msg = q.get(timeout=15)
                yield msg
            except Exception:
                yield ": keep-alive\n\n"
    finally:
        unregister(q)