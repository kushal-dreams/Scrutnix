import json
import queue
import threading
from flask import Blueprint, Response

live_feed_bp = Blueprint('live_feed', __name__, url_prefix='/api')

_event_queue = []
_listeners = []
_lock = threading.Lock()


def push_event(event_data):
    with _lock:
        _event_queue.append(event_data)
        if len(_event_queue) > 50:
            _event_queue.pop(0)

        dead = []
        for q in _listeners:
            try:
                q.put_nowait(event_data)
            except:
                dead.append(q)

        for q in dead:
            _listeners.remove(q)


def event_stream():
    q = queue.Queue()

    with _lock:
        _listeners.append(q)

    try:
        with _lock:
            for event in _event_queue[-10:]:
                yield f"data: {json.dumps(event)}\n\n"

        while True:
            try:
                event = q.get(timeout=30)
                yield f"data: {json.dumps(event)}\n\n"
            except queue.Empty:
                yield ": keepalive\n\n"
    finally:
        with _lock:
            if q in _listeners:
                _listeners.remove(q)


@live_feed_bp.route('/live-feed')
def live_feed():
    return Response(
        event_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
        }
    )
