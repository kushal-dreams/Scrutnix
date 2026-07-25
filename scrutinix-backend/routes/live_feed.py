"""
Live Feed — Server-Sent Events (SSE) for real-time report ticker

GET /api/live-feed — SSE stream of new report events

Uses an in-memory queue (last 50 events).
When a new report is submitted, push_event() is called.
"""

import json
import time
import queue
import threading
from flask import Blueprint, Response

live_feed_bp = Blueprint('live_feed', __name__, url_prefix='/api')

# In-memory event store
_event_queue = []
_listeners = []
_lock = threading.Lock()


def push_event(event_data):
    """
    Push a new event to all connected SSE listeners.
    Called from report submission route.

    event_data should be a dict like:
    {
        'type': 'SMS',
        'identifier': '+91-98XX-XX5678',
        'category': 'Job Fraud'
    }
    """
    with _lock:
        _event_queue.append(event_data)
        # Keep only last 50 events
        if len(_event_queue) > 50:
            _event_queue.pop(0)

        # Notify all listeners
        dead = []
        for q in _listeners:
            try:
                q.put_nowait(event_data)
            except:
                dead.append(q)

        for q in dead:
            _listeners.remove(q)


def event_stream():
    """Generator that yields SSE events"""
    q = queue.Queue()

    with _lock:
        _listeners.append(q)

    try:
        # Send recent events first
        with _lock:
            for event in _event_queue[-10:]:
                yield f"data: {json.dumps(event)}\n\n"

        # Then wait for new events
        while True:
            try:
                event = q.get(timeout=30)
                yield f"data: {json.dumps(event)}\n\n"
            except queue.Empty:
                # Send keepalive
                yield ": keepalive\n\n"
    finally:
        with _lock:
            if q in _listeners:
                _listeners.remove(q)


@live_feed_bp.route('/live-feed')
def live_feed():
    """SSE endpoint — frontend connects with EventSource"""
    return Response(
        event_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
        }
    )
